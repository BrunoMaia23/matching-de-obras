# matching-de-obras

[![testes](https://github.com/BrunoMaia23/matching-de-obras/actions/workflows/testes.yml/badge.svg)](https://github.com/BrunoMaia23/matching-de-obras/actions/workflows/testes.yml)

Um parceiro manda, em planilha, a lista de obras musicais que usou, e cada linha precisa ser ligada a
uma obra do catálogo. O título vem sem acento ou com "(Ao Vivo)", o autor vem como "Lima, Ana" ou "A.
Lima", às vezes falta um autor, às vezes a obra nem existe no catálogo. Este repositório é a lógica de
casamento que montei para um intercâmbio desses no trabalho, reescrita com dados fictícios.

*Short version in English: matching a partner's spreadsheet of music works against an internal catalog. Text
normalization, an inverted index for candidates (with typo correction), explainable scores, and three
outcomes: matched, needs review, or pending. A synthetic answer key measures every change. Synthetic data.*

## O caminho de uma linha

1. **Entrada** (`entrada.py`). O parceiro usa dois formatos: uma linha por obra, com os participantes
   separados por ";", ou uma linha por participante. O segundo é pivotado para o primeiro. Cada linha
   ganha um hash do conteúdo e a staging só aceita hash novo, então planilha reenviada não duplica nada.
2. **Normalização** (`normalizacao.py`). Caixa, acento, pontuação, "(Ao Vivo)", "- Remix", "feat.
   Fulano" saem do título; "Lima, Ana" vira "ANA LIMA". Vírgula não separa lista de nomes, justamente
   por causa do nome invertido.
3. **Candidatos** (`candidatos.py`). Comparar cada linha com o catálogo inteiro não escala. Um índice
   invertido por palavra do título, pesado pela raridade da palavra, traz os 30 mais prováveis. Palavra
   que não existe no vocabulário do catálogo é trocada pela mais parecida antes da busca.
4. **Pontuação** (`pontuacao.py`). De 0 a 100, separada em título e autores para dar para explicar a
   nota. Sem autor de um dos lados, a nota fica limitada e a linha nunca casa sozinha.
5. **Decisão** (`decisao.py`). Casa automaticamente só com nota alta e com folga para o segundo
   candidato. Se a nota é razoável ou dois candidatos ficam colados, a linha vai para revisão com os
   três melhores. Abaixo disso, fica pendente.
6. **Saída** (`saida.py`). Uma planilha com as abas Casadas, Duvidas (com os três candidatos e as notas),
   Pendentes e Resumo, que é o que a área de negócio revisa.

## Para ver funcionando

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m matching demo
```

```
[dados]      catálogo com 3000 obras; 400 linhas do parceiro em 2 planilhas (340 existem no catálogo, 60 são novas)
[entrada]    lote_1.xlsx: 220 linhas novas, 0 já recebidas
[entrada]    lote_2.xlsx: 180 linhas novas, 0 já recebidas
[entrada]    lote_1.xlsx: 0 linhas novas, 220 já recebidas
[casamento]  400 linhas contra 3000 obras em 0.2s: 311 casadas, 32 em dúvida, 57 pendentes
[saída]      resultado.xlsx com as abas Casadas, Duvidas, Pendentes e Resumo
[gabarito]   casadas certas: 311 de 311 (100.0%); das 340 que existem no catálogo, 311 casaram sozinhas, 29 foram para revisão e 0 ficaram pendentes
[gabarito]   das 60 obras novas, 0 casaram por engano
```

O gerador de dados guarda a resposta certa de cada linha (`gabarito.csv`). As obras novas usam o mesmo
vocabulário de títulos do catálogo, de propósito, porque título igual com autor diferente é exatamente o
caso que não pode virar casamento automático. Os números acima são de dados sintéticos e são otimistas;
o que vale é ter uma régua para medir cada mudança.

## O que o gabarito pegou

Na primeira rodada da demo, enquanto eu montava este repositório, as casadas deram 99,3% de acerto,
e o gabarito mostrou dois problemas de verdade:

- Obras que existiam no catálogo ficaram pendentes por causa de um erro de digitação numa palavra
  ("Riacho da Jangaad"). A obra certa nem entrava na lista de candidatos, porque só a palavra comum
  ("Riacho") batia. Daí a correção da palavra pelo vocabulário antes da busca.
- Duas obras novas, de título com uma palavra só, casaram com obras de outra pessoa de mesmo sobrenome
  ("Zélia Queiroz" contra "Wagner Queiroz"). A comparação de nomes passou a tratar pessoa como nome e
  sobrenome: os dois precisam bater, e sobreposição parcial vale pouco.

Os dois casos viraram teste.

## O que muda no trabalho

- O catálogo é muito maior, então o casamento roda em Spark sobre os dados do catálogo no Hadoop. A
  lógica de normalização, candidatos e nota é a mesma.
- A staging fica no banco, com o hash por linha, e cada envio do parceiro tem o seu código de controle.
- Além do casamento, o retorno ao parceiro leva informações calculadas por regras de negócio
  específicas do contrato, que ficaram fora daqui.
