import pytest

from pedido import calcular_total


# ---------------------------------------------------------------------------
# Sem desconto
# ---------------------------------------------------------------------------

class TestSemDesconto:
    def test_pedido_abaixo_de_200_sem_vip_sem_cupom(self):
        assert calcular_total(100.00) == 100.00

    def test_pedido_logo_abaixo_do_limite(self):
        assert calcular_total(199.99) == 199.99

    def test_pedido_zerado(self):
        assert calcular_total(0.0) == 0.0

    def test_parametros_padrao(self):
        assert calcular_total(150.00) == calcular_total(150.00, vip=False, cupom=0.0)


# ---------------------------------------------------------------------------
# Desconto de 10% para pedidos a partir de R$ 200,00
# ---------------------------------------------------------------------------

class TestDescontoPorValor:
    def test_pedido_exatamente_200_recebe_10_por_cento(self):
        assert calcular_total(200.00) == 180.00

    def test_pedido_acima_de_200_recebe_10_por_cento(self):
        assert calcular_total(500.00) == 450.00

    def test_pedido_logo_acima_do_limite(self):
        assert calcular_total(200.01) == 180.01

    @pytest.mark.parametrize(
        "subtotal, esperado",
        [
            (199.99, 199.99),  # sem desconto
            (200.00, 180.00),  # limite inclusivo
            (1000.00, 900.00),
        ],
    )
    def test_limite_do_desconto(self, subtotal, esperado):
        assert calcular_total(subtotal) == esperado


# ---------------------------------------------------------------------------
# Desconto de 5% para clientes VIP
# ---------------------------------------------------------------------------

class TestDescontoVip:
    def test_vip_abaixo_de_200_recebe_apenas_5_por_cento(self):
        assert calcular_total(100.00, vip=True) == 95.00

    def test_vip_logo_abaixo_do_limite(self):
        assert calcular_total(199.99, vip=True) == 189.99

    def test_vip_a_partir_de_200_acumula_descontos(self):
        # A implementação soma os percentuais: 10% + 5% = 15%
        assert calcular_total(200.00, vip=True) == 170.00

    def test_vip_pedido_alto_acumula_descontos(self):
        assert calcular_total(1000.00, vip=True) == 850.00

    def test_nao_vip_explicito(self):
        assert calcular_total(100.00, vip=False) == 100.00


# ---------------------------------------------------------------------------
# Cupom de valor fixo
# ---------------------------------------------------------------------------

class TestCupom:
    def test_cupom_abaixo_de_200(self):
        assert calcular_total(100.00, cupom=20.00) == 80.00

    def test_cupom_zero_nao_altera_valor(self):
        assert calcular_total(100.00, cupom=0.0) == 100.00

    def test_cupom_igual_ao_subtotal_zera_pedido(self):
        assert calcular_total(50.00, cupom=50.00) == 0.0

    def test_cupom_com_desconto_por_valor(self):
        # O cupom é abatido antes do percentual: (300 - 50) * 0.90
        assert calcular_total(300.00, cupom=50.00) == 225.00

    def test_cupom_com_vip(self):
        # (150 - 50) * 0.95
        assert calcular_total(150.00, vip=True, cupom=50.00) == 95.00

    def test_cupom_com_vip_e_desconto_por_valor(self):
        # (400 - 100) * 0.85
        assert calcular_total(400.00, vip=True, cupom=100.00) == 255.00


# ---------------------------------------------------------------------------
# Arredondamento para 2 casas decimais
# ---------------------------------------------------------------------------

class TestArredondamento:
    def test_resultado_tem_no_maximo_2_casas(self):
        resultado = calcular_total(123.456)
        assert resultado == round(resultado, 2)

    def test_arredonda_resultado_com_vip(self):
        # 33.33 * 0.95 = 31.6635 -> 31.66
        assert calcular_total(33.33, vip=True) == 31.66

    def test_arredonda_resultado_com_desconto_por_valor(self):
        # 333.33 * 0.90 = 299.997 -> 300.00
        assert calcular_total(333.33) == 300.00

    def test_arredonda_com_todos_os_descontos(self):
        # (250.55 - 10.10) * 0.85 = 204.3825 -> 204.38
        assert calcular_total(250.55, vip=True, cupom=10.10) == 204.38

    def test_retorna_float(self):
        assert isinstance(calcular_total(100), float)


# ---------------------------------------------------------------------------
# Casos em que o código diverge de uma leitura literal das regras.
# Marcados como xfail(strict=True): quando o comportamento for corrigido,
# o pytest acusará XPASS e o marcador deverá ser removido.
# ---------------------------------------------------------------------------

class TestRegrasAmbiguas:
    @pytest.mark.xfail(
        strict=True,
        reason="O limite de R$ 200 é verificado após o cupom; a regra fala "
        "em 'pedidos a partir de R$ 200', o que sugere o subtotal.",
    )
    def test_cupom_nao_deve_tirar_o_pedido_da_faixa_de_desconto(self):
        # Leitura literal: subtotal 210 >= 200 -> 10% sobre (210 - 20) = 171.00
        # Código atual: 190 < 200 -> sem desconto = 190.00
        assert calcular_total(210.00, cupom=20.00) == 171.00

    @pytest.mark.xfail(
        strict=True,
        reason="Um cupom maior que o subtotal gera total negativo.",
    )
    def test_cupom_maior_que_subtotal_nao_gera_valor_negativo(self):
        assert calcular_total(30.00, cupom=50.00) == 0.0
