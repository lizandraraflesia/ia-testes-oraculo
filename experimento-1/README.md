# Experimento: o teste que confirma o bug

Material de apoio do post estendido **"O teste que confirma o bug: experimentos sobre testes gerados por IA e o papel do QA"** (Conecta CESAR, 2026).

## Pergunta

Quando uma IA gera testes unitários **a partir do código**, e o código tem um bug, os testes expõem o bug ou o confirmam?

## Montagem

**Requisito de negócio:** pedidos a partir de R$ 100,00 recebem 10% de desconto. O valor final é arredondado para 2 casas decimais.

**Código com bug proposital** (`desconto.py`): usa `>` em vez de `>=`, então um pedido de exatamente R$ 100,00 fica sem desconto.

```python
def calcular_desconto(total):
    """Calcula o valor final do pedido com desconto."""
    if total > 100:
        return round(total * 0.9, 2)
    return total
```

A docstring não menciona a regra, para não dar a resposta à IA.

## Cenários

| Cenário | O que a IA recebe | Prompt |
|---|---|---|
| A | Só o código | `prompt_A.txt` |
| B | Código + requisito | `prompt_B.txt` |
| C | Só o requisito, sem a implementação | `prompt_C.txt` |

Cada cenário rodou **3 vezes**, cada vez numa sessão nova e independente (LLMs não são determinísticos). Os testes gerados estão em `runs/` (`A1.py` … `C3.py`), exatamente como a IA respondeu.

- **Ferramenta:** Claude Code 2.1.326, em modo não interativo (`claude -p "<prompt>"`)
- **Modelo:** claude-opus-5-5
- **Data:** 17/11/2026

## Medições

Para cada suíte gerada, `analyze.py` roda o pytest:

1. no **código com bug**, com cobertura de linhas e ramos (`pytest-cov`);
2. no **código corrigido** (`>=`);
3. em **6 mutantes** do código com bug (`>`→`>=`, `>`→`<`, `100`→`101`, `0.9`→`1.9`, arredondar com 3 casas, `return total`→`return None`). Um mutante é "morto" quando ao menos um teste falha.

```bash
pip install pytest pytest-cov
python3 analyze.py .      # gera results.json (rodar dentro desta pasta)
```

## Resultados

| Cenário | No código com bug | No código corrigido | Detectou o bug? | Cobertura | Mutantes mortos |
|---|---|---|---|---|---|
| A (só código) | 3/3 suítes 100% verdes | 3/3 suítes com 2–3 falhas | **Não (0/3)** | 100% | 6/6 |
| B (código + requisito) | 1–3 falhas | todas verdes | Sim (3/3) | 100% | 5/6* |
| C (só requisito) | 2–3 falhas | todas verdes | Sim (3/3) | 100% | 5/6* |

\* O mutante que "sobrevive" em B e C é `>`→`>=`, que é justamente a correção do bug. Os testes desses cenários esperam o comportamento correto, então passam nele.

As três suítes do cenário A contêm a asserção `calcular_desconto(100) == 100`. Em A1, o teste se chama `test_limite_exato_de_100_nao_recebe_desconto`.

## O que isso mostra

- **A cobertura não distingue** as suítes que confirmam o bug das que o pegam: todas tiveram 100%.
- **O teste de mutação também não**: as suítes do cenário A mataram todos os mutantes, inclusive o que corrige o bug. Mutação mede se os testes reagem a mudanças, não se o resultado esperado está certo.
- **As suítes do cenário A bloqueariam a correção:** falham quando o bug é consertado.
- **O requisito no prompt resolveu este caso**, mas aqui ele era curto, claro e o bug estava exatamente no limite descrito. Requisitos reais costumam ser mais ambíguos.

## Limitações

Uma função, um modelo, 9 execuções. É uma demonstração do mecanismo, não um estudo científico. Para reproduzir com outro assistente (Copilot, Gemini etc.), use os mesmos prompts e rode `analyze.py` sobre os testes gerados.

## Arquivos

- `desconto.py`: função com bug
- `prompt_A.txt`, `prompt_B.txt`, `prompt_C.txt`: prompts usados
- `runs/`: testes gerados pela IA (9 suítes)
- `analyze.py`: script de medição
- `results.json`: resultados brutos
- `pytest_A1.txt`: saída do pytest da suíte A1 (base da Figura 1)
- `figura1.png`: Figura 1 do post
