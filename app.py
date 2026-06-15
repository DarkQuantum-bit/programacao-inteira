import streamlit as st
import numpy as np
import pulp
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import io
import time

# CONFIGURAÇÃO DE INTERFACE
st.set_page_config(
    page_title="Otimização de portfólio - MILP",
    page_icon=":bar_chart:",
    layout="wide",  
    initial_sidebar_state="expanded"
)

# Estilização CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }
    div[data-testid="stMetricValue"] {
        color: #00D2FF !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: #8892B0 !important;
    }
    h1, h2, h3, h4 {
        color: #00A3FF !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stDataFrame {
        border: 1px solid #1E293B;
    }
    .stButton>button {
        background-color: #1E293B !important;
        color: #00D2FF !important;
        border: 1px solid #00A3FF !important;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00A3FF !important;
        color: #0E1117 !important;
        box-shadow: 0 0 10px #00D2FF;
    }
    </style>
""", unsafe_allow_html=True)

# PARÂMETROS E MODELAGEM DADOS
def obter_dados_originais():
    return pd.DataFrame({
        "Projeto": [f"P{i}" for i in range(1, 11)],
        "Custo (k)": [180, 140, 260, 110, 90, 170, 100, 150, 210, 130],
        "Valor (k)": [320, 250, 500, 190, 170, 310, 180, 280, 390, 240],
        "Risco": [4, 2, 5, 2, 1, 3, 1, 3, 4, 2],
        "TI (h)": [400, 350, 500, 180, 80, 250, 220, 240, 420, 140],
        "Marketing (h)": [120, 40, 20, 30, 10, 200, 0, 180, 20, 70],
        "Dados (h)": [50, 120, 300, 220, 20, 90, 40, 100, 150, 80],
        "Categoria": ["Inovação", "Infraestrutura", "Inovação", "Dados", "Sustentabilidade", 
                      "Inovação", "Segurança", "Dados", "Infraestrutura", "Sustentabilidade"]
    })

# SUBPROBLEMA: RELAXAÇÃO LINEAR
def resolver_relaxacao_dinamica(df, limites, lambd, fixados, coef_obj):
    prob = pulp.LpProblem("Relaxacao_Linear", pulp.LpMaximize)
    x = [pulp.LpVariable(f"x_{i+1}", lowBound=0, upBound=1) for i in range(10)]
    
    # Função Objetivo: Maximização do retorno ponderado pelo risco
    prob += pulp.lpSum(coef_obj[i] * x[i] for i in range(10))
    
    # Restrições de capacidade e limites estruturais
    prob += pulp.lpSum(df.loc[i, "Custo (k)"] * x[i] for i in range(10)) <= limites["B"]
    prob += pulp.lpSum(df.loc[i, "TI (h)"] * x[i] for i in range(10)) <= limites["A_TI"]
    prob += pulp.lpSum(df.loc[i, "Marketing (h)"] * x[i] for i in range(10)) <= limites["A_M"]
    prob += pulp.lpSum(df.loc[i, "Dados (h)"] * x[i] for i in range(10)) <= limites["A_D"]
    prob += pulp.lpSum(df.loc[i, "Risco"] * x[i] for i in range(10)) <= limites["R_max"]
    
    # Restrições lógicas e dependências entre projetos
    prob += x[2] <= x[3]          
    prob += x[5] <= x[7]          
    prob += x[1] + x[8] <= 1      
    prob += x[6] == 1             
    prob += x[4] + x[9] >= 1      
    prob += x[0] + x[2] + x[5] <= 2  

    # Fixação de variáveis para os nós do Branch-and-Bound
    for idx, val in fixados.items():
        prob += x[idx] == val

    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    if pulp.LpStatus[prob.status] == "Optimal":
        return prob.objective.value(), [x[i].varValue for i in range(10)]
    return None, None

# ALGORITMO E ESTRUTURA DO BRANCH-AND-BOUND
class NoBB:
    def __init__(self, id_no, pai_id=None, fixados=None, decisao="", nivel=0):
        self.id_no = id_no
        self.pai_id = pai_id
        self.fixados = fixados if fixados is not None else {}
        self.decisao = decisao
        self.nivel = nivel
        self.x_pos = 0.0  
        self.y_pos = -float(nivel) * 1.5
        self.status = "Pendente"
        self.z = None
        self.solucao = None
        self.filho_esq = None
        self.filho_dir = None

def estruturar_e_posicionar_arvore(arvore_nos):
    # Inicializa ponteiros de ramificação dos nós ativos
    for no in arvore_nos.values():
        no.filho_esq = None
        no.filho_dir = None
        
    # Mapeia as conexões com base nas decisões de ramificação (0 ou 1)
    for no in arvore_nos.values():
        if no.pai_id is not None and no.pai_id in arvore_nos:
            pai = arvore_nos[no.pai_id]
            if "=0" in no.decisao:
                pai.filho_esq = no.id_no
            else:
                pai.filho_dir = no.id_no

    larguras_subarvores = {}

    def calcular_largura_recursiva(no_id):
        if no_id is None or no_id not in arvore_nos:
            return 0.0
        no = arvore_nos[no_id]
        if no.filho_esq is None and no.filho_dir is None:
            larguras_subarvores[no_id] = 2.0  
            return 2.0
        
        larg_esq = calcular_largura_recursiva(no.filho_esq)
        larg_dir = calcular_largura_recursiva(no.filho_dir)
        
        larg_total = max(larg_esq + larg_dir, 2.0)
        larguras_subarvores[no_id] = larg_total
        return larg_total

    if 0 in arvore_nos:
        calcular_largura_recursiva(0)

    def definir_x_recursivo(no_id, x_centro):
        if no_id is None or no_id not in arvore_nos:
            return
        no = arvore_nos[no_id]
        no.x_pos = x_centro
        
        if no.filho_esq is not None and no.filho_dir is not None:
            w_esq = larguras_subarvores.get(no.filho_esq, 2.0)
            w_dir = larguras_subarvores.get(no.filho_dir, 2.0)
            offset = (w_esq + w_dir) / 2.0
            
            definir_x_recursivo(no.filho_esq, x_centro - offset / 1.8)
            definir_x_recursivo(no.filho_dir, x_centro + offset / 1.8)
        elif no.filho_esq is not None:
            definir_x_recursivo(no.filho_esq, x_centro - 1.5)
        elif no.filho_dir is not None:
            definir_x_recursivo(no.filho_dir, x_centro + 1.5)

    if 0 in arvore_nos:
        definir_x_recursivo(0, 0.0)

def executar_branch_and_bound_completo(df, limites, lambd, coef_obj):
    arvore_nos = {}
    historico_snapshots = []
    z_incumbente = -float('inf')
    solucao_incumbente = None
    
    raiz = NoBB(id_no=0, nivel=0)
    fila = [raiz]
    arvore_nos[0] = raiz
    
    while fila and len(arvore_nos) < 25:
        no_atual = fila.pop(0)
        
        z, sol = resolver_relaxacao_dinamica(df, limites, lambd, no_atual.fixados, coef_obj)
        no_atual.status = "Processando"
        
        estruturar_e_posicionar_arvore(arvore_nos)
        historico_snapshots.append((dict({k: copy_no(v) for k, v in arvore_nos.items()}), no_atual.id_no, z_incumbente))
        
        if z is None:
            no_atual.status = "Inviavel"
            estruturar_e_posicionar_arvore(arvore_nos)
            historico_snapshots.append((dict({k: copy_no(v) for k, v in arvore_nos.items()}), no_atual.id_no, z_incumbente))
            continue
            
        no_atual.z = z
        no_atual.solucao = sol
        
        if z <= z_incumbente:
            no_atual.status = "Podado por Limite"
            estruturar_e_posicionar_arvore(arvore_nos)
            historico_snapshots.append((dict({k: copy_no(v) for k, v in arvore_nos.items()}), no_atual.id_no, z_incumbente))
            continue
            
        eh_inteira = True
        var_fracionaria = None
        for i, val in enumerate(sol):
            if not np.isclose(val, 0.0, atol=1e-4) and not np.isclose(val, 1.0, atol=1e-4):
                eh_inteira = False
                var_fracionaria = i
                break
                
        if eh_inteira:
            no_atual.status = "Inteira (Viavel)"
            if z > z_incumbente:
                z_incumbente = z
                solucao_incumbente = sol
                no_atual.status = "Melhor Incumbente"
            estruturar_e_posicionar_arvore(arvore_nos)
            historico_snapshots.append((dict({k: copy_no(v) for k, v in arvore_nos.items()}), no_atual.id_no, z_incumbente))
        else:
            no_atual.status = "Fracionaria"
            estruturar_e_posicionar_arvore(arvore_nos)
            historico_snapshots.append((dict({k: copy_no(v) for k, v in arvore_nos.items()}), no_atual.id_no, z_incumbente))
            
            novo_nivel = no_atual.nivel + 1
            
            id_esq = len(arvore_nos)
            no_esq = NoBB(id_no=id_esq, pai_id=no_atual.id_no,
                          fixados={**no_atual.fixados, var_fracionaria: 0},
                          decisao=f"x{var_fracionaria+1}=0", nivel=novo_nivel)
            arvore_nos[id_esq] = no_esq
            fila.append(no_esq)
            
            id_dir = len(arvore_nos)
            no_dir = NoBB(id_no=id_dir, pai_id=no_atual.id_no,
                          fixados={**no_atual.fixados, var_fracionaria: 1},
                          decisao=f"x{var_fracionaria+1}=1", nivel=novo_nivel)
            arvore_nos[id_dir] = no_dir
            fila.append(no_dir)
            
    return arvore_nos, z_incumbente, solucao_incumbente, historico_snapshots

def copy_no(no):
    novo = NoBB(no.id_no, no.pai_id, no.fixados.copy(), no.decisao, no.nivel)
    novo.x_pos = no.x_pos
    novo.y_pos = no.y_pos
    novo.status = no.status
    novo.z = no.z
    novo.solucao = no.solucao
    return novo

# PLOT DA ÁRVORE DE DECISÃO
def renderizar_frame_grafico(snapshot_dados):
    snapshot, no_ativo_id, z_global = snapshot_dados
    
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Renderiza as linhas de ramificação
    for no in snapshot.values():
        if no.pai_id is not None and no.pai_id in snapshot:
            pai = snapshot[no.pai_id]
            ax.plot([pai.x_pos, no.x_pos], [pai.y_pos, no.y_pos], color='#334155', linestyle='-', linewidth=2.0, zorder=1)
            
            mx = (pai.x_pos + no.x_pos) / 2
            my = (pai.y_pos + no.y_pos) / 2
            ax.text(mx, my, no.decisao, color='#A3E635', fontsize=8.5, ha='center', va='center', weight='bold',
                    bbox=dict(facecolor='#0E1117', edgecolor='none', alpha=0.9, pad=1))

    # Define mapeamento de cores conforme o status do nó
    for no in snapshot.values():
        if no.id_no == no_ativo_id and no.status == "Processando":
            cor_no = '#FFD700'  
        elif "Melhor" in no.status:
            cor_no = '#00D2FF'  
        elif "Inviavel" in no.status or "Podado" in no.status:
            cor_no = '#7A1F1D'  
        elif "Inteira" in no.status:
            cor_no = '#1E3A8A'  
        elif "Fracionaria" in no.status:
            cor_no = '#4B5563'  
        else:
            cor_no = '#1F2937'  

        ax.scatter(no.x_pos, no.y_pos, color=cor_no, s=1100, edgecolors='#475569', linewidths=1.5, zorder=2)
        
        val_z = f"\nZ={no.z:.1f}" if no.z is not None else ""
        ax.text(no.x_pos, no.y_pos, f"Nó {no.id_no}{val_z}", color='#E0E6ED', fontsize=8, weight='bold', ha='center', va='center', zorder=3)

    ax.set_title(f"Branch-and-Bound (MILP)\nNó atual: {no_ativo_id} | Z = {z_global:.2f}", 
                 color='#00A3FF', fontsize=14, weight='bold', pad=15)
    
    plt.axis('off')
    
    if snapshot:
        x_coords = [no.x_pos for no in snapshot.values()]
        y_coords = [no.y_pos for no in snapshot.values()]
        ax.set_xlim(min(x_coords) - 1.8, max(x_coords) + 1.8)
        ax.set_ylim(min(y_coords) - 0.8, 0.5)
        
    return fig

# STREAMLIT
st.title("Otimização de portfólio de projetos")
st.subheader("Seleção de projetos via Programação Linear Inteira Mista (MILP)")

st.markdown("---")

st.sidebar.header("Parâmetros do modelo")
st.sidebar.subheader("Ponderação de risco")
perfil = st.sidebar.selectbox("Configuração de perfil", ["Conservador", "Moderado", "Agressivo"])

if perfil == "Conservador":
    lambd_atual = 30
    descricao_perfil = "Penalização estrita por risco e volatilidade."
elif perfil == "Moderado":
    lambd_atual = 15
    descricao_perfil = "Balanço padrão entre retorno esperado e variância."
else:
    lambd_atual = 2
    descricao_perfil = "Foco em retorno bruto com tolerância alta ao risco."

st.sidebar.caption(fr"**Fator $\lambda$: {lambd_atual}** — *{descricao_perfil}*")

st.sidebar.subheader("Restrições de recursos")
b_orcamento = st.sidebar.slider("Orçamento total (k)", 400, 2000, 850, step=50)
cap_ti = st.sidebar.slider("Horas disponíveis - TI", 500, 2500, 1800, step=100)
cap_mkt = st.sidebar.slider("Horas disponíveis - Marketing", 100, 1200, 500, step=50)
cap_dados = st.sidebar.slider("Horas disponíveis - Dados", 100, 1500, 900, step=100)
risco_maximo = st.sidebar.slider("Teto de risco acumulado", 5, 35, 15, step=1)

limites_dict = {
    "B": b_orcamento,
    "A_TI": cap_ti,
    "A_M": cap_mkt,
    "A_D": cap_dados,
    "R_max": risco_maximo
}

df_projetos = obter_dados_originais()
coef_obj_dinamico = [v - lambd_atual * r for v, r in zip(df_projetos["Valor (k)"], df_projetos["Risco"])]

st.markdown("### Projetos")
st.dataframe(df_projetos.style.background_gradient(cmap="Blues", subset=["Valor (k)", "Custo (k)"]), use_container_width=True)

# Processamento do Branch-and-Bound
arvore, z_otimo, solucao, passos = executar_branch_and_bound_completo(df_projetos, limites_dict, lambd_atual, coef_obj_dinamico)

st.markdown("---")
st.markdown("### Solução ótima encontrada")

if solucao is None or z_otimo == -float('inf'):
    st.error("Instância inviável para as restrições selecionadas. Altere os limites na barra lateral.")
else:
    indices_selecionados = [i for i, val in enumerate(solucao) if val > 0.5]
    df_selecionados = df_projetos.iloc[indices_selecionados].copy()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Função objetivo (Z)", f"{z_otimo:.2f}")
    col2.metric("Valor total retornado", f"{df_selecionados['Valor (k)'].sum()}k")
    col3.metric("Orçamento utilizado", f"{df_selecionados['Custo (k)'].sum()}k / {b_orcamento}k")
    col4.metric("Risco acumulado", f"{df_selecionados['Risco'].sum()} / {risco_maximo}")
    
    st.markdown("#### Projetos selecionados")
    st.dataframe(df_selecionados, use_container_width=True)

    st.markdown("---")
    st.markdown("### Execução do Branch-and-Bound")
    st.markdown("Visualização")

    if passos:
        chave_cenario = f"{perfil}_{b_orcamento}_{cap_ti}_{cap_mkt}_{cap_dados}_{risco_maximo}"
        if "chave_anterior" not in st.session_state or st.session_state.chave_anterior != chave_cenario:
            st.session_state.chave_anterior = chave_cenario
            st.session_state.passo_atual = 0
            st.session_state.em_execucao = False

        col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
        with col_btn1:
            btn_play = st.button("Iniciar")
        with col_btn2:
            btn_reset = st.button("Reiniciar")

        if btn_reset:
            st.session_state.passo_atual = 0
            st.session_state.em_execucao = False
            st.rerun()

        container_grafico = st.empty()

        if btn_play:
            st.session_state.em_execucao = True
            for idx in range(len(passos)):
                st.session_state.passo_atual = idx
                fig = renderizar_frame_grafico(passos[idx])
                container_grafico.pyplot(fig)
                plt.close(fig)
                time.sleep(0.4)
            st.session_state.em_execucao = False
        else:
            fig_atual = renderizar_frame_grafico(passos[st.session_state.passo_atual])
            container_grafico.pyplot(fig_atual)
            plt.close(fig_atual)
