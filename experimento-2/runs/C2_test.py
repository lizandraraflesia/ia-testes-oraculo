import pytest
from pedido import calcular_total


def valor(x):
    """Compara floats sem sofrer com imprecisão de ponto flutuante."""
    return pytest.approx(x, abs=1e-9)


class TestSemDesconto:
    def test_subtotal_abaixo_de_200_sem_vip_e_sem_cupom(self):
        assert calcular_total(100.00) == valor(100.00)

    def test_valores_padrao_dos_parametros(self):
        assert calcular_total(150.00) == calcular_total(150.00, vip=False, cupom=0.0)

    def test_subtotal_zero(self):
        assert calcular_total(0.0) == valor(0.0)


class TestDescontoPorValor:
    def test_logo_abaixo_do_limite_nao_tem_desconto(self):
        assert calcular_total(199.99) == valor(199.99)

    def test_exatamente_200_recebe_10_por_cento(self):
        # "a partir de R$ 200,00" inclui o próprio 200
        assert calcular_total(200.00) == valor(180.00)

    def test_logo_acima_do_limite_recebe_10_por_cento(self):
        # 200.01 * 0.90 = 180.009
        assert calcular_total(200.01) == valor(180.01)

    def test_valor_alto_recebe_10_por_cento(self):
        assert calcular_total(1000.00) == valor(900.00)


class TestDescontoVip:
    def test_vip_abaixo_de_200_recebe_5_por_cento(self):
        assert calcular_total(100.00, vip=True) == valor(95.00)

    def test_nao_vip_nao_recebe_5_por_cento(self):
        assert calcular_total(100.00, vip=False) == valor(100.00)


class TestCupom:
    def test_cupom_abate_valor_fixo(self):
        assert calcular_total(100.00, cupom=15.00) == valor(85.00)

    def test_cupom_zero_nao_altera_total(self):
        assert calcular_total(100.00, cupom=0.0) == valor(100.00)

    def test_cupom_com_centavos(self):
        assert calcular_total(50.00, cupom=0.99) == valor(49.01)


class TestArredondamento:
    def test_vip_arredonda_para_duas_casas(self):
        # 12.34 * 0.95 = 11.723
        assert calcular_total(12.34, vip=True) == valor(11.72)

    def test_arredonda_para_cima_quando_necessario(self):
        # 333.33 * 0.90 = 299.997
        assert calcular_total(333.33) == valor(300.00)

    @pytest.mark.parametrize(
        "subtotal, vip, cupom",
        [
            (12.34, True, 0.0),
            (333.33, False, 0.0),
            (257.77, True, 3.33),
            (99.99, True, 1.11),
        ],
    )
    def test_resultado_tem_no_maximo_duas_casas(self, subtotal, vip, cupom):
        total = calcular_total(subtotal, vip=vip, cupom=cupom)
        assert round(total, 2) == valor(total)


# ---------------------------------------------------------------------------
# Combinações de descontos: a especificação NÃO define
#   (a) se os percentuais se somam (15%) ou se acumulam (0,90 x 0,95);
#   (b) se o cupom é aplicado antes ou depois dos percentuais.
# Estes testes aceitam qualquer interpretação válida e ainda pegam bugs como
# "ignorar um dos descontos". Quando a regra for confirmada, troque o
# conjunto de valores pelo valor único esperado.
# ---------------------------------------------------------------------------
class TestCombinacoesRegraAConfirmar:
    def test_vip_com_pedido_a_partir_de_200(self):
        total = calcular_total(200.00, vip=True)
        # somados: 200 * 0.85 = 170.00 | acumulados: 200 * 0.90 * 0.95 = 171.00
        assert total in (valor(170.00), valor(171.00))

    def test_pedido_a_partir_de_200_com_cupom(self):
        total = calcular_total(200.00, cupom=20.00)
        # cupom depois: 180 - 20 = 160.00 | cupom antes: (200 - 20) * 0.90 = 162.00
        assert total in (valor(160.00), valor(162.00))

    def test_vip_com_cupom(self):
        total = calcular_total(100.00, vip=True, cupom=10.00)
        # cupom depois: 95 - 10 = 85.00 | cupom antes: 90 * 0.95 = 85.50
        assert total in (valor(85.00), valor(85.50))

    def test_todos_os_descontos_juntos(self):
        total = calcular_total(200.00, vip=True, cupom=10.00)
        possiveis = (
            160.00,  # somados, cupom depois
            161.00,  # acumulados, cupom depois
            161.50,  # somados, cupom antes
            162.45,  # acumulados, cupom antes
        )
        assert total in [valor(v) for v in possiveis]

    def test_todos_os_descontos_juntos_sao_menores_que_cada_um_isolado(self):
        todos = calcular_total(200.00, vip=True, cupom=10.00)
        assert todos < calcular_total(200.00)
        assert todos < calcular_total(200.00, vip=True)
        assert todos < calcular_total(200.00, cupom=10.00)
