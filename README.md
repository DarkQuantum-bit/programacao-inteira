
# Programação Inteira — Otimização de Portfólio de Projetos

**Seleção ótima de projetos sob restrições orçamentárias, operacionais, estratégicas e de risco utilizando Programação Inteira e Branch-and-Bound.**

Projeto de **Pesquisa Operacional e Otimização Combinatória** voltado à seleção de um portfólio de projetos, utilizando **Programação Linear Inteira Binária**, relaxação linear e um algoritmo **Branch-and-Bound** implementado em Python.

A aplicação permite investigar decisões de investimento em um conjunto de projetos com diferentes custos, retornos esperados, níveis de risco e necessidades de recursos humanos.

O sistema utiliza **PuLP e CBC** para resolver os subproblemas de Programação Linear, enquanto uma interface desenvolvida com **Streamlit** permite configurar restrições, analisar as soluções e acompanhar visualmente a evolução da árvore de busca.

## 1. Introdução

A seleção de um portfólio de projetos é um problema de decisão comum em organizações que precisam distribuir recursos limitados entre diferentes oportunidades de investimento.

Cada projeto apresenta características específicas, como:

- Custo de implementação;
- Valor ou retorno esperado;
- Nível de risco;
- Demanda de recursos humanos;
- Categoria estratégica;
- Dependências com outros projetos;
- Restrições de compatibilidade ou exclusividade.

O desafio consiste em determinar quais projetos devem ser executados de modo a maximizar o benefício obtido, respeitando os recursos disponíveis e as regras de negócio.

Esse problema pode ser formulado como um modelo de **Programação Linear Inteira Binária**, no qual cada variável de decisão representa a seleção ou rejeição de um projeto.

Uma das principais dificuldades decorre da natureza discreta dessas decisões.

Diferentemente de problemas de Programação Linear contínua, as soluções precisam respeitar condições de integralidade, o que pode tornar o processo de otimização computacionalmente mais complexo.

Neste projeto, a resolução é realizada por meio de um algoritmo Branch-and-Bound, que combina relaxações lineares, ramificações e procedimentos de poda para explorar o espaço de soluções.

## 2. Descrição do problema

O sistema considera um conjunto de dez projetos candidatos:

```math
P=\{P_1,P_2,\ldots,P_{10}\}
```

Cada projeto possui atributos relacionados ao investimento necessário, benefício esperado, risco e consumo de recursos de três áreas:

- Tecnologia da Informação (TI);
- Marketing;
- Dados.

Além disso, são consideradas relações lógicas entre projetos, incluindo dependências, incompatibilidades, obrigatoriedade e diversidade.

O objetivo é selecionar um subconjunto de projetos que maximize o retorno ajustado por risco, respeitando simultaneamente as restrições financeiras, operacionais e estratégicas.

### 2.1. Dados dos projetos

A implementação utiliza a seguinte instância de dez projetos:

| Projeto | Custo (k) | Valor (k) | Risco | TI (h) | Marketing (h) | Dados (h) |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 180 | 320 | 4 | 400 | 120 | 50 |
| P2 | 140 | 250 | 2 | 350 | 40 | 120 |
| P3 | 260 | 500 | 5 | 500 | 20 | 300 |
| P4 | 110 | 190 | 2 | 180 | 30 | 220 |
| P5 | 90 | 170 | 1 | 80 | 10 | 20 |
| P6 | 170 | 310 | 3 | 250 | 200 | 90 |
| P7 | 100 | 180 | 1 | 220 | 0 | 40 |
| P8 | 150 | 280 | 3 | 240 | 180 | 100 |
| P9 | 210 | 390 | 4 | 420 | 20 | 150 |
| P10 | 130 | 240 | 2 | 140 | 70 | 80 |

Os valores monetários são expressos em milhares de unidades monetárias, identificados por `k`.

Os projetos também pertencem às seguintes categorias:

| Projeto | Categoria |
|---|---|
| P1 | Inovação |
| P2 | Infraestrutura |
| P3 | Inovação |
| P4 | Dados |
| P5 | Sustentabilidade |
| P6 | Inovação |
| P7 | Segurança |
| P8 | Dados |
| P9 | Infraestrutura |
| P10 | Sustentabilidade |

Esses dados são definidos diretamente no código e representam uma instância demonstrativa do problema.

## 3. Fundamentação teórica

### 3.1. Programação Linear Inteira

A Programação Linear Inteira é uma classe de problemas de otimização na qual algumas ou todas as variáveis de decisão precisam assumir valores inteiros.

Uma formulação geral pode ser representada por:

```math
\max \mathbf{c}^{T}\mathbf{x}
```

sujeita a:

```math
A\mathbf{x}\leq\mathbf{b}
```

```math
\mathbf{x}\in\mathbb{Z}^{n}
```

onde:

- `x` representa o vetor de variáveis de decisão;
- `c` representa o vetor de coeficientes da função objetivo;
- `A` representa a matriz de restrições;
- `b` representa o vetor de limites;
- `Z` representa o conjunto dos números inteiros.

Quando as variáveis são restritas aos valores zero e um, o problema pertence à classe de Programação Inteira Binária.

### 3.2. Variáveis binárias

Uma variável binária representa uma decisão com duas possibilidades:

```math
x_i\in\{0,1\}
```

No problema de seleção de projetos:

```math
x_i=
\begin{cases}
1,&\text{se o projeto }i\text{ for selecionado}\\
0,&\text{caso contrário}
\end{cases}
```

Essa representação permite modelar decisões de investimento, dependências e restrições lógicas.

### 3.3. Relaxação linear

Uma técnica fundamental na resolução de problemas inteiros consiste em remover temporariamente a restrição de integralidade.

Assim, em vez de exigir:

```math
x_i\in\{0,1\}
```

considera-se:

```math
0\leq x_i\leq1
```

O problema resultante é uma **relaxação linear**.

Para problemas de maximização, a solução ótima da relaxação fornece um limite superior para a solução inteira do mesmo subproblema.

Esse princípio é utilizado pelo algoritmo Branch-and-Bound para avaliar regiões do espaço de busca.

### 3.4. Branch-and-Bound

O algoritmo *Branch-and-Bound* é um método de otimização exata baseado na exploração sistemática de subproblemas.

Seu funcionamento combina três operações principais.

**Branching — Ramificação**

Um subproblema é dividido em novos subproblemas mediante a imposição de restrições adicionais.

**Bounding — Limitação**

A relaxação linear fornece limites para o valor que pode ser obtido em cada subproblema.

**Pruning — Poda**

Subproblemas são descartados quando não podem produzir soluções melhores que a melhor solução inteira conhecida ou quando são inviáveis.

O processo permite reduzir o número de soluções que precisam ser examinadas explicitamente.

Quando executado até a conclusão, com regras corretas de limitação e poda, Branch-and-Bound pode certificar a otimalidade global.

No presente projeto, a implementação estabelece um limite para o tamanho da árvore explorada, de modo que o encerramento da execução não implica necessariamente comprovação de otimalidade.

## 4. Formulação matemática

### 4.1. Conjunto de projetos

Considere:

```math
I=\{1,2,\ldots,10\}
```

o conjunto dos projetos candidatos.

### 4.2. Parâmetros

| Parâmetro | Descrição |
|---|---|
| `v_i` | Valor esperado do projeto `i` |
| `c_i` | Custo de implementação |
| `r_i` | Índice de risco |
| `t_i` | Horas de TI necessárias |
| `m_i` | Horas de Marketing necessárias |
| `d_i` | Horas de Dados necessárias |
| `B` | Orçamento máximo disponível |
| `A_TI` | Capacidade disponível de TI |
| `A_M` | Capacidade disponível de Marketing |
| `A_D` | Capacidade disponível de Dados |
| `R_max` | Limite de risco acumulado |
| `λ` | Coeficiente de penalização do risco |

### 4.3. Variáveis de decisão

Para cada projeto, define-se:

```math
x_i\in\{0,1\},\quad i\in I
```

A variável assume valor um quando o projeto é selecionado e zero caso contrário.

### 4.4. Função objetivo

O modelo procura maximizar o valor total dos projetos selecionados, descontando uma penalização associada ao risco.

A função objetivo é:

```math
\max Z=\sum_{i\in I}(v_i-\lambda r_i)x_i
```

Equivalentemente:

```math
Z=
\sum_{i\in I}v_ix_i
-
\lambda\sum_{i\in I}r_ix_i
```

O primeiro termo representa o valor esperado agregado dos projetos selecionados.

O segundo representa a penalização linear associada ao risco.

O coeficiente `λ` controla o compromisso entre retorno e risco.

Quanto maior seu valor, maior a penalização relativa aplicada a projetos com índices de risco elevados.

**Observação:** a implementação não utiliza uma matriz de covariância ou uma formulação estatística de variância. O risco é representado por índices individuais e penalização linear.

### 4.5. Restrição orçamentária

A soma dos custos dos projetos selecionados não pode ultrapassar o orçamento disponível.

```math
\sum_{i\in I}c_ix_i\leq B
```

Essa condição representa o limite financeiro de investimento.

### 4.6. Restrição de capacidade de TI

A demanda total de horas de TI deve respeitar a capacidade disponível.

```math
\sum_{i\in I}t_ix_i\leq A_{\mathrm{TI}}
```

### 4.7. Restrição de capacidade de Marketing

A demanda total de horas de Marketing não pode exceder seu limite.

```math
\sum_{i\in I}m_ix_i\leq A_{\mathrm{M}}
```

### 4.8. Restrição de capacidade de Dados

A demanda agregada da equipe de Dados deve respeitar a capacidade disponível.

```math
\sum_{i\in I}d_ix_i\leq A_{\mathrm{D}}
```

### 4.9. Limite de risco acumulado

O risco total dos projetos selecionados deve permanecer abaixo do limite definido.

```math
\sum_{i\in I}r_ix_i\leq R_{\max}
```

Essa restrição é independente da penalização de risco da função objetivo.

Portanto, o modelo combina duas formas de controle:

1. Penalização do risco no objetivo;
2. Limite máximo de risco admissível.

## 5. Restrições lógicas e estratégicas

Além dos limites financeiros e operacionais, o sistema incorpora relações entre projetos.

### 5.1. Dependência entre P3 e P4

A seleção de P3 exige a seleção de P4.

```math
x_3\leq x_4
```

Assim, P3 não pode ser selecionado isoladamente.

### 5.2. Dependência entre P6 e P8

A seleção de P6 exige a seleção de P8.

```math
x_6\leq x_8
```

### 5.3. Exclusividade entre P2 e P9

Os projetos P2 e P9 não podem ser selecionados simultaneamente.

```math
x_2+x_9\leq1
```

### 5.4. Projeto obrigatório

O projeto P7 deve obrigatoriamente integrar o portfólio.

```math
x_7=1
```

### 5.5. Seleção mínima entre P5 e P10

Pelo menos um dos projetos P5 e P10 deve ser selecionado.

```math
x_5+x_{10}\geq1
```

Essa condição permite selecionar ambos, caso a solução seja viável.

### 5.6. Limite para projetos de Inovação

No máximo dois dos projetos P1, P3 e P6 podem ser selecionados.

```math
x_1+x_3+x_6\leq2
```

Essa restrição limita a concentração do portfólio nessa categoria.

### 5.7. Síntese da formulação

O problema completo é:

```math
\max Z=\sum_{i=1}^{10}(v_i-\lambda r_i)x_i
```

Sujeito a:

```math
\begin{aligned}
\sum_{i=1}^{10}c_ix_i &\leq B\\
\sum_{i=1}^{10}t_ix_i &\leq A_{\mathrm{TI}}\\
\sum_{i=1}^{10}m_ix_i &\leq A_{\mathrm{M}}\\
\sum_{i=1}^{10}d_ix_i &\leq A_{\mathrm{D}}\\
\sum_{i=1}^{10}r_ix_i &\leq R_{\max}\\
x_3&\leq x_4\\
x_6&\leq x_8\\
x_2+x_9&\leq1\\
x_7&=1\\
x_5+x_{10}&\geq1\\
x_1+x_3+x_6&\leq2
\end{aligned}
```

Com:

```math
x_i\in\{0,1\},\quad i=1,\ldots,10
```

Essa formulação caracteriza um problema de **Programação Linear Inteira Binária**, com restrições de recursos e relações lógicas entre decisões.

## 6. Implementação computacional

A aplicação foi desenvolvida em Python e concentra suas funcionalidades no arquivo `app.py`.

O código combina:

- Modelagem matemática com PuLP;
- Resolução de relaxações lineares com CBC;
- Construção da árvore Branch-and-Bound;
- Registro de estados intermediários da busca;
- Visualização gráfica com Matplotlib;
- Interface interativa com Streamlit.

### 6.1. Relaxação linear com PuLP

Cada nó da árvore Branch-and-Bound representa um subproblema de Programação Linear.

A implementação cria o modelo utilizando:

```python
prob = pulp.LpProblem(
    "Relaxacao_Linear",
    pulp.LpMaximize
)
```

As variáveis são inicialmente definidas no intervalo contínuo entre zero e um:

```python
x = [
    pulp.LpVariable(
        f"x_{i+1}",
        lowBound=0,
        upBound=1
    )
    for i in range(10)
]
```

Essa definição corresponde à relaxação das variáveis binárias.

A função objetivo é construída usando os coeficientes previamente calculados:

```python
prob += pulp.lpSum(
    coef_obj[i] * x[i]
    for i in range(10)
)
```

As restrições financeiras, operacionais e lógicas são adicionadas ao modelo.

### 6.2. Fixação de variáveis

Durante a ramificação, certas variáveis são fixadas em zero ou um.

O código adiciona essas condições por meio de:

```python
for idx, val in fixados.items():
    prob += x[idx] == val
```

Cada conjunto de fixações representa um nó da árvore de busca.

### 6.3. Resolução das relaxações

Os subproblemas são resolvidos utilizando CBC:

```python
prob.solve(
    pulp.PULP_CBC_CMD(msg=False)
)
```

Quando o solver encontra uma solução ótima para a relaxação, são recuperados o valor da função objetivo e os valores das variáveis.

Caso contrário, o subproblema não produz uma solução utilizada pela busca.

## 7. Algoritmo Branch-and-Bound

O projeto implementa uma estrutura própria de busca, representada pela função:

```python
executar_branch_and_bound_completo(
    df,
    limites,
    lambd,
    coef_obj
)
```

### 7.1. Nó da árvore

Cada nó é representado por uma instância da classe `NoBB`.

Essa estrutura armazena informações como:

- Identificador do nó;
- Nó pai;
- Variáveis fixadas;
- Decisão de ramificação;
- Profundidade;
- Status;
- Valor da relaxação linear;
- Solução encontrada;
- Posição para visualização.

Essa organização permite acompanhar o desenvolvimento da árvore e identificar as decisões realizadas pelo algoritmo.

### 7.2. Estratégia de exploração

A implementação utiliza uma fila de nós pendentes.

A cada iteração, o primeiro nó da fila é selecionado para processamento.

Essa organização corresponde a uma exploração em largura, conhecida como *Breadth-First Search* (BFS).

O algoritmo segue, conceitualmente, as etapas:

1. Criar o nó raiz;
2. Resolver sua relaxação linear;
3. Verificar a viabilidade;
4. Comparar o limite superior com a solução incumbente;
5. Verificar se a solução é inteira;
6. Atualizar a incumbente quando aplicável;
7. Ramificar sobre uma variável fracionária;
8. Inserir os subproblemas na fila;
9. Repetir enquanto houver nós disponíveis e o limite de exploração permitir.

### 7.3. Solução incumbente

A incumbente representa a melhor solução inteira encontrada até determinado momento.

Seu valor é iniciado por:

```math
Z_{\mathrm{inc}}=-\infty
```

Quando uma nova solução inteira viável é encontrada com valor superior à incumbente, ela substitui a solução anterior.

### 7.4. Poda por inviabilidade

Quando a relaxação linear de determinado nó não possui solução viável, o subproblema é descartado.

Isso ocorre porque a imposição de restrições adicionais não pode recuperar a viabilidade de uma região já inviável.

### 7.5. Poda por limite

Para um problema de maximização, a relaxação linear fornece um limite superior para a melhor solução inteira do nó.

Se:

```math
Z_{\mathrm{LP}}\leq Z_{\mathrm{inc}}
```

então o subproblema não pode melhorar a incumbente conhecida.

Nesse caso, ele pode ser podado.

### 7.6. Identificação de soluções inteiras

A implementação verifica se todas as variáveis estão suficientemente próximas de zero ou um.

É utilizada uma tolerância numérica:

```python
np.isclose(
    val,
    0.0,
    atol=1e-4
)
```

e uma verificação equivalente para o valor um.

Quando todas as variáveis satisfazem o critério, a solução é considerada inteira pela implementação.

### 7.7. Ramificação

Quando uma solução fracionária é identificada, o algoritmo seleciona a primeira variável fracionária encontrada.

Suponha que essa variável seja:

```math
0<x_k<1
```

A ramificação produz dois subproblemas:

**Ramo esquerdo:**

```math
x_k=0
```

**Ramo direito:**

```math
x_k=1
```

Ambos herdam as restrições anteriores e incorporam a nova fixação.

### 7.8. Limite de exploração

A implementação estabelece uma condição de limitação baseada no número de nós criados.

O laço principal utiliza:

```python
while fila and len(arvore_nos) < 25:
```

Como a ramificação cria dois nós por vez, a quantidade final de nós registrados pode ultrapassar o limite indicado.

Essa configuração mantém a árvore relativamente pequena para visualização.

Entretanto, a busca pode ser interrompida antes de examinar todos os subproblemas relevantes.

Consequentemente, o valor apresentado corresponde à melhor solução inteira encontrada durante a exploração realizada.

**A implementação não garante comprovação de otimalidade global quando a busca é interrompida pelo limite de nós.**

## 8. Visualização da árvore Branch-and-Bound

Um dos recursos centrais do projeto é a visualização da evolução do algoritmo de otimização.

A aplicação utiliza Matplotlib para representar a árvore de decisões.

### 8.1. Estrutura gráfica

Cada nó é representado por um círculo contendo:

- Identificador;
- Valor da função objetivo da relaxação, quando disponível.

As conexões representam as decisões de ramificação, associadas à fixação de variáveis em zero ou um.

A posição dos nós é calculada recursivamente para organizar visualmente as subárvores.

### 8.2. Estados dos nós

A visualização diferencia os nós conforme o estado da busca.

Entre os estados utilizados estão:

- Pendente;
- Processando;
- Inviável;
- Podado por limite;
- Fracionária;
- Inteira viável;
- Melhor incumbente.

Essa classificação permite acompanhar os principais acontecimentos durante a exploração do espaço de soluções.

### 8.3. Histórico da busca

O sistema registra diferentes estados da árvore ao longo da execução.

Esses registros são armazenados como snapshots, incluindo:

- Estrutura dos nós;
- Nó ativo;
- Estado de processamento;
- Valor da melhor incumbente.

Os snapshots permitem reconstruir a evolução visual do algoritmo.

### 8.4. Animação

A interface possui controles para iniciar e reiniciar a apresentação da árvore.

A sequência de snapshots é exibida com um intervalo de aproximadamente 0,4 segundo entre os quadros.

Essa funcionalidade oferece uma representação didática dos processos de ramificação, limitação e poda.

## 9. Interface interativa

A aplicação utiliza Streamlit para permitir a configuração dos parâmetros do modelo.

### 9.1. Perfis de risco

O usuário pode selecionar três perfis:

| Perfil | Penalização do risco |
|---|---:|
| Conservador | 30 |
| Moderado | 15 |
| Agressivo | 2 |

O coeficiente escolhido modifica a função objetivo:

```math
\max Z=\sum_{i=1}^{10}(v_i-\lambda r_i)x_i
```

Um coeficiente maior penaliza mais fortemente os projetos com índices elevados de risco.

O perfil conservador prioriza maior penalização do risco.

O perfil agressivo atribui maior importância relativa ao valor bruto dos projetos.

### 9.2. Configuração dos recursos

Os parâmetros disponíveis na interface são:

| Parâmetro | Mínimo | Máximo | Padrão |
|---|---:|---:|---:|
| Orçamento total (k) | 400 | 2000 | 850 |
| Capacidade de TI (h) | 500 | 2500 | 1800 |
| Capacidade de Marketing (h) | 100 | 1200 | 500 |
| Capacidade de Dados (h) | 100 | 1500 | 900 |
| Risco acumulado máximo | 5 | 35 | 15 |

Esses parâmetros podem ser alterados por controles deslizantes.

A cada alteração, o modelo é reconstruído e o algoritmo é executado novamente.

### 9.3. Visualização dos projetos

A aplicação apresenta uma tabela com os dados originais dos dez projetos.

As colunas de custo e valor recebem uma formatação visual para facilitar a comparação.

### 9.4. Resultados da otimização

Quando uma solução inteira é encontrada, a aplicação apresenta:

- Valor da função objetivo;
- Valor agregado dos projetos selecionados;
- Orçamento utilizado;
- Risco acumulado;
- Tabela dos projetos selecionados;
- Visualização da árvore Branch-and-Bound.

Caso não seja encontrada uma solução inteira durante a exploração, a interface apresenta uma mensagem de inviabilidade.

Essa mensagem deve ser interpretada com cautela, pois uma busca limitada pode não encontrar uma solução mesmo quando existe um portfólio viável fora dos nós examinados.

## 10. Estrutura do repositório

```text
programacao-inteira/
│
├── app.py
├── requirements.txt
└── README.md
```

### Arquivos principais

| Arquivo | Descrição |
|---|---|
| `app.py` | Formulação matemática, algoritmo Branch-and-Bound, interface e visualizações |
| `requirements.txt` | Dependências necessárias para execução |
| `README.md` | Documentação do projeto |

A implementação está concentrada em um único arquivo Python.

## 11. Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem principal |
| PuLP | Modelagem e resolução das relaxações lineares |
| CBC | Solver de Programação Linear |
| NumPy | Operações numéricas e verificações de integralidade |
| Pandas | Organização dos dados dos projetos |
| Streamlit | Interface web interativa |
| Matplotlib | Visualização da árvore Branch-and-Bound |
| Pillow | Biblioteca de manipulação de imagens incluída nas dependências |

## 12. Instalação e execução

### 12.1. Pré-requisitos

- Python 3;
- Pip;
- Ambiente virtual recomendado;
- Dependências listadas em `requirements.txt`.

### 12.2. Clonar o repositório

```bash
git clone https://github.com/DarkQuantum-bit/programacao-inteira.git
```

Acesse o diretório:

```bash
cd programacao-inteira
```

### 12.3. Criar ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

### 12.4. Instalar dependências

```bash
python -m pip install -r requirements.txt
```

### 12.5. Executar a aplicação

```bash
streamlit run app.py
```

O Streamlit disponibilizará a interface em um endereço local, normalmente:

http://localhost:8501

### 12.6. Utilização

1. Selecione um perfil de risco;
2. Configure o orçamento disponível;
3. Defina os limites de horas de TI, Marketing e Dados;
4. Ajuste o teto de risco acumulado;
5. Analise o portfólio encontrado;
6. Examine os projetos selecionados;
7. Utilize o controle **Iniciar** para visualizar a árvore Branch-and-Bound;
8. Utilize **Reiniciar** para retornar ao início da animação.

## 13. Análise experimental

O projeto permite investigar diferentes características do problema de seleção de portfólio.

### 13.1. Influência do orçamento

Aumentar ou reduzir o orçamento disponível permite analisar como a restrição financeira modifica o conjunto de projetos selecionados.

### 13.2. Sensibilidade ao risco

A comparação entre os perfis conservador, moderado e agressivo permite investigar alterações na composição do portfólio em função da penalização do risco.

### 13.3. Limitações de recursos humanos

A redução das capacidades de TI, Marketing ou Dados permite estudar como gargalos operacionais alteram a seleção de projetos.

### 13.4. Dependências e exclusividades

As restrições lógicas permitem analisar situações em que um projeto depende de outro ou em que duas oportunidades são mutuamente incompatíveis.

### 13.5. Complexidade da busca

A visualização da árvore permite investigar:

- Quantidade de nós criados;
- Profundidade das ramificações;
- Nós inviáveis;
- Podas por limite;
- Soluções inteiras encontradas;
- Evolução da incumbente.

Essas análises ajudam a compreender o funcionamento do Branch-and-Bound em problemas de seleção binária.

## 14. Limitações da implementação

O projeto possui finalidade acadêmica e demonstrativa.

Entre suas principais limitações estão:

**Instância fixa:** são considerados dez projetos com parâmetros definidos diretamente no código.

**Retornos determinísticos:** os valores esperados são tratados como parâmetros conhecidos.

**Risco simplificado:** o modelo utiliza índices de risco e uma penalização linear, sem modelagem estatística de incerteza ou correlação entre projetos.

**Restrição de recursos estática:** as horas disponíveis são tratadas como capacidades agregadas, sem um cronograma temporal de execução dos projetos.

**Limite de nós:** a árvore Branch-and-Bound possui um limite de exploração, podendo encerrar a busca antes da comprovação de otimalidade.

**Escolha de ramificação:** o algoritmo utiliza a primeira variável fracionária encontrada, sem estratégias avançadas de seleção.

**Busca em largura:** a exploração utiliza uma fila FIFO, sem priorização dos nós por melhor limite.

**Relaxações independentes:** cada nó constrói e resolve um novo modelo linear, sem reutilização explícita de bases ou informações internas do solver.

**Ausência de certificado final:** o sistema não apresenta um indicador de gap de otimalidade ou uma certificação de que toda a árvore relevante foi explorada.

Essas limitações devem ser consideradas na interpretação dos resultados.

## 15. Possíveis extensões

O projeto pode ser ampliado em diferentes direções:

- Remoção do limite fixo de exploração;
- Implementação de limites de tempo configuráveis;
- Cálculo do gap de otimalidade;
- Estratégias de seleção de nós por melhor limite;
- Heurísticas de escolha das variáveis de ramificação;
- Comparação com o Branch-and-Bound interno de solvers MILP;
- Inclusão de cortes válidos e técnicas de Branch-and-Cut;
- Importação de projetos por arquivos CSV;
- Seleção de projetos em múltiplos períodos;
- Modelagem de precedências temporais;
- Incorporação de riscos estocásticos;
- Otimização multiobjetivo;
- Análise de fronteiras entre retorno e risco;
- Exportação do portfólio selecionado e dos indicadores;
- Testes automatizados das restrições e soluções.

Essas extensões permitiriam explorar problemas mais complexos de alocação de recursos e gestão de portfólios.

## 16. Referências

### Programação Inteira

**Wolsey, L. A. (1998).**

*Integer Programming.*

John Wiley & Sons.

### Otimização Inteira Mista

**Conforti, M., Cornuéjols, G., & Zambelli, G. (2014).**

*Integer Programming.*

Springer.

https://doi.org/10.1007/978-3-319-11008-0

### Pesquisa Operacional e Programação Linear

**Bertsimas, D., & Tsitsiklis, J. N. (1997).**

*Introduction to Linear Optimization.*

Athena Scientific.

### Otimização Combinatória

**Schrijver, A. (2003).**

*Combinatorial Optimization: Polyhedra and Efficiency.*

Springer.

### PuLP

**PuLP — Python Linear Programming.**

Documentação oficial:

https://coin-or.github.io/pulp/

### CBC

**COIN-OR Branch-and-Cut (CBC).**

Documentação do solver:

https://github.com/coin-or/Cbc

### Streamlit

**Streamlit Developers.**

Documentação oficial:

https://docs.streamlit.io/

As referências apresentam fundamentos relacionados à modelagem e à implementação, não necessariamente a bibliografia originalmente utilizada no desenvolvimento acadêmico.

## 17. Contexto acadêmico

Este projeto apresenta uma aplicação de **Programação Inteira à seleção de portfólios de projetos**, integrando modelagem matemática, algoritmos de otimização e visualização computacional.

O trabalho aborda conceitos de:

- Pesquisa Operacional;
- Programação Linear;
- Programação Linear Inteira Binária;
- Otimização Combinatória;
- Algoritmos Branch-and-Bound;
- Relaxações Lineares;
- Modelagem de Restrições Lógicas;
- Alocação de Recursos;
- Análise de Decisão;
- Computação Científica.

A implementação combina a formulação de um problema de decisão com o desenvolvimento de um procedimento explícito de busca e uma interface voltada à análise e compreensão de seus resultados.

O repositório possui finalidade acadêmica, educacional e demonstrativa.

---

**Programação Inteira — Otimização de Portfólio de Projetos**

*Pesquisa Operacional · Otimização Combinatória · Branch-and-Bound · Python*
