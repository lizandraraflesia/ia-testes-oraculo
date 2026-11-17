"""
Testes unitários para calcular_total(subtotal, vip=False, cupom=0.0).

Regras do requisito:
  R1. Pedidos a partir de R$ 200,00 recebem 10% de desconto.
  R2. Clientes VIP recebem 5% de desconto.
  R3. Cupom de desconto com valor fixo em reais.
  R4. Valor final arredondado para 2 casas decimais.

Os testes marcados com @pytest.mark.premissa dependem de pontos que o
requisito NÃO define (ver docstring de cada um). Para rodar só os
testes das regras explícitas:  pytest -m "not premissa"

Registre o marcador no pytest.ini / pyproject.toml para evitar warnings:
  [pytest]
  markers =
      premissa: teste depende de regra ambígua/não especificada
"""

import pytest

from pedido import calcular_total


def assert_valor(obtido, esperado):
    """Compara valores monetários com tolerância mínima de ponto flutuante."""
    assert obtido == pytest.approx(esperado, abs=1e-9)


# ---------------------------------------------------------------------------
# Regras explícitas
# ---------------------------------------------------------------------------

class TestSemDesconto:
    def test_pedido_abaixo_de_200_sem_vip_sem_cupom_nao_tem_desconto(self):
        assert_valor(calcular_total(100.00), 100.00)

    def test_valores_padrao_dos_parametros(self):
        assert_valor(calcular_total(150.00), calcular_total(150.00, vip=False, cupom=0.0))

    def test_subtotal_zero(self):
        assert_valor(calcular_total(0.00), 0.00)


class TestDescontoPorValor:
    """R1 - 10% a partir de R$ 200,00."""

    def test_limite_inferior_exato_200_recebe_desconto(self):
        assert_valor(calcular_total(200.00), 180.00)

    def test_imediatamente_abaixo_do_limite_nao_recebe_desconto(self):
        assert_valor(calcular_total(199.99), 199.99)

    def test_imediatamente_acima_do_limite_recebe_desconto(self):
        # 200.01 * 0.90 = 180.009 -> 180.01
        assert_valor(calcular_total(200.01), 180.01)

    @pytest.mark.parametrize(
        "subtotal, esperado",
        [
            (250.00, 225.00),
            (1000.00, 900.00),
            (333.33, 300.00),  # 299.997 -> 300.00
        ],
    )
    def test_desconto_de_10_por_cento_acima_do_limite(self, subtotal, esperado):
        assert_valor(calcular_total(subtotal), esperado)


class TestDescontoVip:
    """R2 - VIP recebe 5%."""

    def test_vip_abaixo_de_200_recebe_5_por_cento(self):
        assert_valor(calcular_total(100.00, vip=True), 95.00)

    def test_vip_logo_abaixo_do_limite_recebe_apenas_5_por_cento(self):
        # 199.99 * 0.95 = 189.9905 -> 189.99
        assert_valor(calcular_total(199.99, vip=True), 189.99)

    def test_nao_vip_explicito_nao_recebe_desconto(self):
        assert_valor(calcular_total(100.00, vip=False), 100.00)


class TestCupom:
    """R3 - cupom de valor fixo (casos sem desconto percentual envolvido)."""

    def test_cupom_subtrai_valor_fixo(self):
        assert_valor(calcular_total(100.00, cupom=10.00), 90.00)

    def test_cupom_com_centavos(self):
        assert_valor(calcular_total(100.00, cupom=0.01), 99.99)

    def test_cupom_zero_nao_altera_total(self):
        assert_valor(calcular_total(100.00, cupom=0.0), 100.00)

    def test_cupom_igual_ao_subtotal_zera_o_total(self):
        assert_valor(calcular_total(50.00, cupom=50.00), 0.00)


class TestArredondamento:
    """R4 - resultado com 2 casas decimais."""

    @pytest.mark.parametrize(
        "subtotal, vip, cupom",
        [
            (12.34, True, 0.0),
            (199.99, True, 0.0),
            (200.01, False, 0.0),
            (0.1, False, 0.0),
            (123.456, False, 0.0),
            (0.3, False, 0.1),
        ],
    )
    def test_resultado_tem_no_maximo_duas_casas_decimais(self, subtotal, vip, cupom):
        resultado = calcular_total(subtotal, vip=vip, cupom=cupom)
        assert_valor(resultado, round(resultado, 2))

    def test_arredonda_para_baixo(self):
        # 12.34 * 0.95 = 11.723 -> 11.72
        assert_valor(calcular_total(12.34, vip=True), 11.72)

    def test_arredonda_para_cima(self):
        # 200.01 * 0.90 = 180.009 -> 180.01
        assert_valor(calcular_total(200.01), 180.01)

    def test_subtotal_com_mais_de_duas_casas_sem_desconto(self):
        assert_valor(calcular_total(123.456), 123.46)

    def test_erro_classico_de_ponto_flutuante_e_corrigido(self):
        # 0.3 - 0.1 = 0.19999999999999998 em float
        assert_valor(calcular_total(0.3, cupom=0.1), 0.20)


# ---------------------------------------------------------------------------
# Premissas — o requisito não define esses comportamentos
# ---------------------------------------------------------------------------

@pytest.mark.premissa
class TestCombinacaoDeDescontos:
    def test_vip_com_pedido_acima_de_200_descontos_sao_cumulativos_e_somados(self):
        """
        AMBÍGUO: os descontos se acumulam? De que forma?
          - somados (15%):      200 * 0.85        = 170.00  <- premissa adotada
          - sequenciais:        200 * 0.90 * 0.95 = 171.00
          - só o maior (10%):   200 * 0.90        = 180.00
        """
        assert_valor(calcular_total(200.00, vip=True), 170.00)

    def test_cupom_aplicado_apos_desconto_percentual(self):
        """
        AMBÍGUO: o cupom entra antes ou depois do percentual?
          - depois: 100 * 0.95 - 10 = 85.00  <- premissa adotada
          - antes:  (100 - 10) * 0.95 = 85.50
        """
        assert_valor(calcular_total(100.00, vip=True, cupom=10.00), 85.00)

    def test_faixa_de_200_considera_subtotal_antes_do_cupom(self):
        """
        AMBÍGUO: o limite de R$ 200 vale para o subtotal bruto ou já com cupom?
          - subtotal bruto: 210 * 0.90 - 20 = 169.00  <- premissa adotada
          - após cupom:     210 - 20 = 190 (< 200, sem desconto) = 190.00
        """
        assert_valor(calcular_total(210.00, cupom=20.00), 169.00)

    def test_todos_os_descontos_juntos(self):
        # Premissas acima: 300 * 0.85 - 15 = 240.00
        assert_valor(calcular_total(300.00, vip=True, cupom=15.00), 240.00)


@pytest.mark.premissa
class TestCasosLimiteNaoEspecificados:
    def test_cupom_maior_que_total_nao_gera_valor_negativo(self):
        """AMBÍGUO: premissa = total mínimo é 0.00 (nunca negativo)."""
        assert_valor(calcular_total(30.00, cupom=50.00), 0.00)

    def test_subtotal_negativo_lanca_erro(self):
        """AMBÍGUO: premissa = entrada inválida gera ValueError."""
        with pytest.raises(ValueError):
            calcular_total(-10.00)

    def test_cupom_negativo_lanca_erro(self):
        """AMBÍGUO: premissa = cupom negativo (que aumentaria o total) gera ValueError."""
        with pytest.raises(ValueError):
            calcular_total(100.00, cupom=-5.00)
