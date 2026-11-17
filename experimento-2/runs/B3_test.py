import pytest

from pedido import calcular_total


# ---------------------------------------------------------------------------
# Sem desconto
# ---------------------------------------------------------------------------

def test_pedido_abaixo_de_200_sem_vip_sem_cupom_nao_tem_desconto():
    assert calcular_total(100.0) == 100.0


def test_subtotal_zero_retorna_zero():
    assert calcular_total(0.0) == 0.0


def test_cliente_nao_vip_explicito_nao_recebe_desconto():
    assert calcular_total(100.0, vip=False) == 100.0


# ---------------------------------------------------------------------------
# Desconto de 10% para pedidos a partir de R$ 200,00
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "subtotal, esperado",
    [
        (199.99, 199.99),  # logo abaixo do limite: sem desconto
        (200.00, 180.00),  # exatamente no limite: 10%
        (200.01, 180.01),  # logo acima: 200.01 * 0.90 = 180.009 -> 180.01
        (250.00, 225.00),  # bem acima do limite
    ],
)
def test_fronteira_do_desconto_de_10_por_cento(subtotal, esperado):
    assert calcular_total(subtotal) == esperado


# ---------------------------------------------------------------------------
# Desconto VIP de 5%
# ---------------------------------------------------------------------------

def test_cliente_vip_abaixo_de_200_recebe_5_por_cento():
    assert calcular_total(100.0, vip=True) == 95.0


def test_cliente_vip_a_partir_de_200_acumula_descontos():
    # 10% + 5% = 15% sobre 200,00 -> 170,00
    assert calcular_total(200.0, vip=True) == 170.0


# ---------------------------------------------------------------------------
# Cupom de valor fixo
# ---------------------------------------------------------------------------

def test_cupom_e_abatido_do_valor():
    assert calcular_total(150.0, cupom=20.0) == 130.0


def test_cupom_zero_nao_altera_valor():
    assert calcular_total(150.0, cupom=0.0) == 150.0


def test_cupom_igual_ao_subtotal_zera_o_pedido():
    assert calcular_total(50.0, cupom=50.0) == 0.0


def test_cupom_que_leva_pedido_abaixo_de_200_remove_desconto_de_10():
    # 220 - 30 = 190 -> não atinge o limite de 200
    assert calcular_total(220.0, cupom=30.0) == 190.0


def test_cupom_que_mantem_pedido_em_200_preserva_desconto_de_10():
    # 250 - 50 = 200 -> 200 * 0.90 = 180
    assert calcular_total(250.0, cupom=50.0) == 180.0


def test_vip_com_cupom_aplica_percentual_sobre_valor_apos_cupom():
    # 100 - 20 = 80 -> 80 * 0.95 = 76
    assert calcular_total(100.0, vip=True, cupom=20.0) == 76.0


def test_todos_os_descontos_combinados():
    # 300 - 50 = 250 -> 250 * 0.85 = 212.50
    assert calcular_total(300.0, vip=True, cupom=50.0) == 212.5


# ---------------------------------------------------------------------------
# Arredondamento para 2 casas decimais
# ---------------------------------------------------------------------------

def test_resultado_arredondado_para_duas_casas_com_vip():
    # 199.99 * 0.95 = 189.9905 -> 189.99
    assert calcular_total(199.99, vip=True) == 189.99


def test_resultado_arredondado_para_duas_casas_com_desconto_de_10():
    # 333.33 * 0.90 = 299.997 -> 300.00
    assert calcular_total(333.33) == 300.0


def test_retorno_e_float():
    assert isinstance(calcular_total(100), float)


# ---------------------------------------------------------------------------
# Caso que as regras não cobrem (comportamento a confirmar)
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    strict=True,
    reason="Regra não definida: cupom maior que o subtotal gera total negativo",
)
def test_cupom_maior_que_subtotal_nao_deve_gerar_total_negativo():
    # Hoje: 30 - 50 = -20 -> retorna -20.0
    assert calcular_total(30.0, cupom=50.0) >= 0.0
