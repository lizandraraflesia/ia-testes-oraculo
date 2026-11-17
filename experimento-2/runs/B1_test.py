import pytest

from pedido import calcular_total


# ---------------------------------------------------------------------------
# Sem desconto
# ---------------------------------------------------------------------------

def test_pedido_abaixo_de_200_sem_vip_sem_cupom_nao_tem_desconto():
    assert calcular_total(100.00) == 100.00


def test_pedido_de_valor_zero_retorna_zero():
    assert calcular_total(0.00) == 0.00


# ---------------------------------------------------------------------------
# Desconto de 10% para pedidos a partir de R$ 200,00
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "subtotal, esperado",
    [
        (199.99, 199.99),  # logo abaixo do limite: sem desconto
        (200.00, 180.00),  # exatamente no limite: "a partir de" inclui 200
        (200.01, 180.01),  # logo acima do limite
        (500.00, 450.00),
    ],
)
def test_desconto_de_10_por_cento_a_partir_de_200(subtotal, esperado):
    assert calcular_total(subtotal) == esperado


# ---------------------------------------------------------------------------
# Desconto de 5% para clientes VIP
# ---------------------------------------------------------------------------

def test_cliente_vip_abaixo_de_200_recebe_5_por_cento():
    assert calcular_total(100.00, vip=True) == 95.00


def test_cliente_nao_vip_nao_recebe_desconto_vip():
    assert calcular_total(100.00, vip=False) == 100.00


def test_cliente_vip_logo_abaixo_de_200_recebe_apenas_5_por_cento():
    # 199.99 * 0.95 = 189.9905 -> 189.99
    assert calcular_total(199.99, vip=True) == 189.99


def test_cliente_vip_a_partir_de_200_acumula_descontos():
    # 10% (valor) + 5% (VIP) = 15% -> 200 * 0.85 = 170.00
    assert calcular_total(200.00, vip=True) == 170.00


# ---------------------------------------------------------------------------
# Cupom de desconto com valor fixo em reais
# ---------------------------------------------------------------------------

def test_cupom_e_subtraido_do_valor_do_pedido():
    assert calcular_total(100.00, cupom=20.00) == 80.00


def test_cupom_zero_nao_altera_o_valor():
    assert calcular_total(100.00, cupom=0.0) == 100.00


def test_cupom_igual_ao_subtotal_zera_o_pedido():
    assert calcular_total(50.00, cupom=50.00) == 0.00


def test_cupom_com_cliente_vip_abaixo_de_200():
    # (100 - 20) * 0.95 = 76.00
    assert calcular_total(100.00, vip=True, cupom=20.00) == 76.00


def test_cupom_com_pedido_que_continua_acima_de_200():
    # (300 - 50) * 0.90 = 225.00
    assert calcular_total(300.00, cupom=50.00) == 225.00


def test_todos_os_descontos_combinados():
    # (300 - 50) * 0.85 = 212.50
    assert calcular_total(300.00, vip=True, cupom=50.00) == 212.50


# ---------------------------------------------------------------------------
# Arredondamento para 2 casas decimais
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "subtotal, vip, cupom, esperado",
    [
        (33.33, True, 0.0, 31.66),      # 33.33 * 0.95 = 31.6635
        (222.22, False, 0.0, 200.00),   # 222.22 * 0.90 = 199.998
        (123.45, True, 10.10, 107.68),  # 113.35 * 0.95 = 107.6825
        (250.00, True, 0.0, 212.50),    # 250 * 0.85 = 212.5
    ],
)
def test_valor_final_arredondado_para_2_casas(subtotal, vip, cupom, esperado):
    resultado = calcular_total(subtotal, vip=vip, cupom=cupom)
    assert resultado == esperado


# ---------------------------------------------------------------------------
# Regras ambíguas / possíveis defeitos
# Estes testes seguem a leitura literal das regras e FALHAM com a
# implementação atual. Confirmar o comportamento esperado com o PO.
# ---------------------------------------------------------------------------

def test_limite_de_200_considera_o_subtotal_antes_do_cupom():
    # Regra: "Pedidos a partir de R$ 200,00 recebem 10% de desconto".
    # O pedido é de R$ 210,00; o cupom não deveria tirar o direito ao desconto.
    # Esperado: (210 - 20) * 0.90 = 171.00
    # Atual: o limite é verificado após o cupom (190 < 200) -> 190.00
    assert calcular_total(210.00, cupom=20.00) == 171.00


def test_cupom_maior_que_subtotal_nao_gera_valor_negativo():
    # Um pedido não deveria ter total negativo.
    # Atual: 50 - 80 = -30.00
    assert calcular_total(50.00, cupom=80.00) == 0.00
