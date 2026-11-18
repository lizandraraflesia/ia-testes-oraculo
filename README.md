# O teste que confirma o bug: experimentos

[![Reproduzir experimentos](https://github.com/lizandraraflesia/ia-testes-oraculo/actions/workflows/experimentos.yml/badge.svg)](https://github.com/lizandraraflesia/ia-testes-oraculo/actions/workflows/experimentos.yml)

Material de apoio do post estendido **"O teste que confirma o bug: experimentos sobre testes gerados por IA e o papel do QA"** (Conecta CESAR, 2026).

- [`experimento-1/`](experimento-1/README.md): função com bug de fronteira (`>` em vez de `>=`). A IA gera testes a partir do código, do código + requisito ou só do requisito. Base da Figura 1 e do Quadro 1 do post.
- [`experimento-2/`](experimento-2/README.md): requisito realista com lacunas (faixa, VIP e cupom). A IA sinaliza as lacunas? Qual interpretação os testes congelam? Base da caixa "Mas não basta dar o requisito para a IA?".

Ferramenta: Claude Code 2.1.326 (modelo claude-opus-5-5), em 17/11/2026. São demonstrações pequenas do mecanismo, não estudos científicos.

## Reproduzir

```bash
pip install pytest pytest-cov
cd experimento-1 && python3 analyze.py . && cd ..
cd experimento-2 && python3 analyze.py . && cd ..
```

A cada alteração, o GitHub Actions roda os dois scripts e confere se os resultados batem com os publicados em `results.json` (selo no topo desta página).
