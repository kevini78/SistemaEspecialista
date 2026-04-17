# Sistema Especialista para Diagnóstico de Doenças Respiratórias

Este é um protótipo feito em Python que ajuda a diferenciar seis doenças
comuns com sintomas parecidos: resfriado, gripe, H1N1, COVID-19, dengue
e sinusite. O usuário marca a intensidade de cada sintoma, clica num
botão, e o sistema devolve a hipótese mais provável junto com uma
recomendação de conduta.

> Importante: o sistema foi feito para fins de estudo. Não serve como
> diagnóstico real nem substitui consulta médica.

---

## Por que esse problema?

A escolha veio de uma observação bem prática: quando alguém começa a se
sentir mal, os primeiros sintomas quase sempre se sobrepõem. Febre,
dor de cabeça, cansaço e dor no corpo aparecem em praticamente todas
as doenças da nossa lista. Diferenciar uma da outra depende de detalhes
(velocidade com que a doença começa, presença de manchas na pele,
perda de olfato, dor atrás dos olhos etc.) e de como esses sinais se
combinam.

Esse tipo de raciocínio “se acontece isso **e** isso, então
provavelmente é aquilo” é exatamente o que um sistema especialista
faz bem. Por isso o problema encaixou no escopo da disciplina.

---

## A tabela que serviu de base

Toda a base de conhecimento saiu da tabela abaixo, que foi o ponto de
partida do trabalho:

| Sintoma / Critério | Resfriado | Gripe (Influenza) | H1N1 | COVID-19 | Dengue | Sinusite |
|---|---|---|---|---|---|---|
| Início dos sintomas | Gradual | Súbito | Súbito (rápido) | Variável | Súbito | Gradual |
| Febre | Rara | Alta (38–39 °C) | Muito alta (>39 °C) | Moderada | Muito alta (>39 °C) | Rara |
| Dor de cabeça | Leve | Moderada | Intensa | Moderada | Muito intensa | Intensa (face) |
| Dor atrás dos olhos | Não | Raro | Raro | Raro | Muito comum | Comum |
| Dor muscular | Leve | Intensa | Muito intensa | Moderada | Muito intensa | Leve |
| Cansaço / fadiga | Leve | Intenso | Extremo | Moderado | Extremo | Moderado |
| Tosse | Leve | Seca | Seca intensa | Seca persistente | Rara | Com catarro |
| Coriza | Comum | Às vezes | Pouco comum | Comum | Raro | Muito comum |
| Congestão nasal | Comum | Moderada | Leve | Comum | Raro | Intensa |
| Dor de garganta | Comum | Moderada | Moderada | Comum | Raro | Moderada |
| Falta de ar | Raro | Raro | Pode ocorrer | Comum | Raro | Raro |
| Perda de olfato/paladar | Não | Não | Não | Muito comum | Não | Pode ocorrer |
| Manchas na pele | Não | Não | Não | Raro | Comum | Não |
| Sintomas respiratórios | Leves | Fortes | Muito fortes | Fortes | Quase ausentes | Fortes |
| Náusea / vômito | Raro | Às vezes | Comum | Às vezes | Comum | Raro |
| Duração média | 3–5 dias | 7–10 dias | 7–14 dias | 5–14 dias | 5–10 dias | >10 dias |

A ideia foi transformar cada célula dessa tabela em uma regra que o
sistema consulta na hora de decidir.

---

## Como o sistema “pensa”

O raciocínio tem três camadas, cada uma resolvendo um problema
específico:

**1. A pessoa descreve o que sente em linguagem humana.**
Ninguém normalmente fala “minha dor de cabeça está em 0,7”. A gente
diz “está meio forte”, “tá leve”, “tá insuportável”. Então os níveis
de intensidade do sistema são rótulos (ausente, muito leve, leve,
moderado, intenso, muito intenso) e cada rótulo tem um valor numérico
por trás, entre 0 e 1. Isso é lógica fuzzy.

**2. Cada sintoma é comparado com o que seria esperado pra cada
doença.** Na dengue, por exemplo, o esperado é febre bem alta.
Se a pessoa diz que a febre está moderada, o sintoma “conta” para
dengue, mas não tanto quanto se estivesse muito alta. Essa diferença
é calculada como uma similaridade: `1 − |esperado − observado|`.

**3. As evidências são combinadas.**
Uma doença costuma ter vários sintomas contando a favor (e alguns
contra). Para juntar tudo isso num número só, o sistema usa os
**Fatores de Certeza (CF)** do MYCIN, que é o jeito clássico de
lidar com incerteza em sistemas especialistas. A fórmula de
combinação trata três casos:

- duas evidências positivas se reforçam;
- duas negativas também se reforçam (no sentido contrário);
- uma positiva e uma negativa se cancelam parcialmente.

No final, sobra um número entre −1 e 1 para cada doença. O sistema
mostra o maior como “mais provável” e lista os outros abaixo.

---

## Justificando as escolhas

### Por que sistema especialista e não um modelo de machine learning?

A resposta curta é: porque não existe dataset. Pra treinar um modelo
de ML razoável eu precisaria de milhares de casos rotulados de
“paciente X tinha esses sintomas e o diagnóstico confirmado foi Y”.
Como o trabalho partiu de uma **tabela de referência**, e não de
dados reais, qualquer modelo numérico treinado nela seria um
recorta-e-cola disfarçado. O sistema especialista, ao contrário,
assume desde o início que o conhecimento vem de uma fonte externa
(a tabela, que funciona como um “especialista humano”) e deixa esse
conhecimento **visível** e **editável**.

### Por que regras de produção?

As regras no formato “se... então...” batem diretamente com o jeito
que a tabela está organizada. Cada célula vira uma regra:
“se a febre é muito alta, conta como evidência forte para dengue”.
Isso tem duas vantagens práticas: é legível por um humano (qualquer
pessoa consegue abrir o arquivo `knowledge_base.py` e entender o
que está acontecendo) e é fácil de corrigir. Se amanhã descobrirmos
que a tabela está errada num ponto, basta mudar um número.

### Por que Fatores de Certeza em vez de probabilidades?

Eu cheguei a considerar usar uma rede bayesiana, que seria o caminho
“mais correto” em termos de teoria da probabilidade. O problema é que
pra montar uma rede bayesiana direito eu precisaria das probabilidades
condicionais — algo como “qual a probabilidade de febre dado que é
dengue?”. Esses números não estão na tabela, e inventá-los seria
chutar. Os Fatores de Certeza foram desenhados exatamente pra esse
cenário: quando o especialista consegue dizer “esse sintoma favorece
bastante essa doença”, mas não consegue dar uma probabilidade exata.
Eles também lidam bem com contra-evidência (o peso negativo), o que
ajuda a separar doenças parecidas. Por exemplo, coriza forte
**enfraquece** a hipótese de dengue.

### Por que lógica fuzzy pra intensidade?

A tabela usa termos como “leve”, “moderada”, “intensa”, “muito
intensa”. Tratar isso como booleano (o sintoma está presente ou não)
perderia muita informação: uma dor de cabeça leve é muito diferente
de uma muito intensa, e essa diferença ajuda a separar gripe de
dengue. A lógica fuzzy é o ferramental clássico pra converter
rótulos linguísticos em graus numéricos, então foi uma escolha
quase automática.

### Por que Python + Streamlit?

Python é a linguagem mais usada em cursos de IA, então faz sentido
manter o padrão. Streamlit foi escolhido porque resolve um problema
que geralmente atrapalha trabalhos acadêmicos: **a interface**.
Sem ele, eu teria que separar o projeto em backend e frontend, gastar
tempo com HTML/CSS/JS, e a parte de IA ficaria diluída no meio do
código de interface. Com Streamlit, uma tela decente fica pronta em
poucas dezenas de linhas e todo mundo consegue rodar localmente com
um `pip install` e um comando.

### Por que os pesos estão no código, escritos à mão?

Porque eles vieram diretamente da leitura da tabela. Para cada par
(doença, sintoma) eu atribuí dois valores: o **nível esperado** do
sintoma (ex.: febre muito alta na dengue = 1.0) e um **peso** que
reflete o quanto aquele sintoma ajuda a identificar a doença.
Alguns sintomas são “marcadores” (perda de olfato para COVID,
dor atrás dos olhos para dengue) e ganharam pesos próximos de 0,8.
Outros são inespecíficos (cansaço aparece em todas) e ficaram com
pesos menores. Num trabalho futuro, esses pesos poderiam ser
aprendidos a partir de casos reais, o que conecta o projeto com a
parte de aprendizagem de máquina da disciplina.

---

## Estrutura do projeto

```
sistema-especialista/
├── knowledge_base.py    # A "tabela" traduzida em regras + fuzzy
├── inference_engine.py  # O motor que avalia as regras e combina CFs
├── app.py               # A interface em Streamlit
├── requirements.txt
└── README.md
```

A separação entre **base de conhecimento** e **motor de inferência**
é uma característica clássica de sistemas especialistas: o motor não
sabe nada sobre doenças, ele só sabe avaliar regras. Se amanhã alguém
quiser usar esse mesmo motor para diagnosticar outra coisa
(problemas de carro, plantas, o que for), basta trocar o arquivo de
regras.

---

## Como rodar

Pré-requisitos: Python 3.10 ou superior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre automaticamente em `http://localhost:8501`.
Na tela, você marca a intensidade de cada sintoma clicando nos
botões e depois clica em **Obter diagnóstico**.

---

## Limitações que a gente reconhece

- A base cobre só seis doenças. Qualquer coisa fora disso o sistema
  vai tentar encaixar numa delas, o que obviamente é errado.
- Os pesos foram calibrados olhando a tabela, não dados reais. Então
  os resultados são coerentes com a tabela, mas não necessariamente
  com a realidade clínica.
- O sistema não considera contexto (idade, comorbidades, onde a
  pessoa mora, se está tendo surto de alguma doença na região).
- Sintomas raros, de alarme ou atípicos não entram na conta.

Ou seja: o protótipo mostra como o raciocínio funciona, mas usar isso
pra diagnosticar alguém de verdade seria uma péssima ideia.
