# Experimento 2: requisito com lacunas

## Pergunta

Se a IA recebe o requisito, ela resolve o problema do oráculo? E quando o requisito é incompleto, como quase todo requisito real?

## Montagem

**Requisito** (`requisito.txt`):

> - Pedidos a partir de R$ 200,00 recebem 10% de desconto.
> - Clientes VIP recebem 5% de desconto.
> - O cliente pode aplicar um cupom de desconto com valor fixo em reais.
> - O valor final é arredondado para 2 casas decimais.

O texto deixa **quatro lacunas**:

| Lacuna | Intenção do negócio (PO) | O que o código faz (`pedido.py`) |
|---|---|---|
| G1. A faixa de R$ 200 considera o valor antes ou depois do cupom? | Antes | Depois |
| G2. Desconto de faixa e VIP acumulam? | Não, vale o maior | Somam (15%) |
| G3. O cupom entra antes ou depois dos percentuais? | Depois | Antes |
| G4. O total pode ficar negativo? | Não, mínimo 0 | Pode |

A intenção do PO está em `pedido_intencao_po.py` e **não aparece** no requisito, como acontece na vida real. As duas leituras são compatíveis com o texto. Só G4 tem "cara de bug".

## Cenários

| Cenário | O que a IA recebe | Prompt |
|---|---|---|
| B | Código + requisito | `prompt_B.txt` |
| C | Só o requisito | `prompt_C.txt` |

Diferente do experimento 1, aqui o prompt **não proíbe explicações**, para ver se a IA sinaliza as lacunas. São 3 execuções por cenário, em sessões independentes, com Claude Code 2.1.326 e o modelo claude-opus-5-5, em 17/11/2026.

- `runs/B1.md` … `runs/C3.md`: respostas completas da IA (texto + código)
- `runs/*_test.py`: só o código de testes extraído de cada resposta

## Resultados

**A IA sinalizou lacunas nas 6 respostas.** Todas avisaram que o requisito não define algo e pediram confirmação. As respostas do cenário C listaram as lacunas de forma mais completa.

**Mas cada suíte já vem com uma escolha feita.** Rodando cada suíte contra o código e contra a intenção do PO:

| Suíte | Contra o código | Testes que contradizem a intenção do PO |
|---|---|---|
| B1 | 2 falhas (G1 e G4, marcadas como possíveis bugs) | 7 |
| B2 | todas passam (2 xfail: G1 e G4) | 6 |
| B3 | todas passam (1 xfail: G4) | 5 |
| C1 | 6 falhas | 4 |
| C2 | 3 falhas | 3 |
| C3 | 5 falhas | 4 |

Em B2 e B3, um teste a mais aparece como falha no pytest quando roda contra a intenção do PO: é um `xfail(strict=True)` sobre o total negativo que **passa**, e o pytest conta isso como falha (XPASS estrito). Esse teste concorda com o PO, por isso não entra na contagem acima. O `results.json` separa os dois casos (`falhas` e `xpass_estrito`).

Por lacuna:

- **G2 (acumular descontos):** as 3 suítes do cenário B seguiram o código (soma). No cenário C, 2 suítes escolheram somar e 1 aceitou "somar ou cascata". **Nenhuma** adotou a regra do negócio, "vale o maior" (C1 a citou como uma das possibilidades).
- **G3 (ordem do cupom):** as 3 suítes do cenário B seguiram o código.
- **G1 (faixa antes/depois do cupom):** no B, 2 suítes trataram como possível bug e 1 seguiu o código. No C, as 3 escolheram "antes", que coincide com o PO.
- **G4 (total negativo):** tratado como bug ou deixado em aberto em todas. Nenhuma suíte congelou o valor negativo.

## O que isso mostra

1. A IA é **boa para achar lacunas** no requisito. Vale pedir isso explicitamente.
2. Mas o aviso fica **no texto da resposta**, e o teste vem com uma interpretação. Com o código no contexto, nas lacunas "sem cara de bug", essa interpretação é a do código.
3. Nenhum palpite acerta uma regra que só existe na cabeça do PO. Fechar a lacuna é uma decisão humana.

## Reproduzir

```bash
pip install pytest
python3 analyze.py .      # roda as 6 suítes contra pedido.py e pedido_intencao_po.py e gera results.json
```
