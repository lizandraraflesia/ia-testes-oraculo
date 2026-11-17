import pytest

from desconto import calcular_desconto


# --- Pedidos abaixo de R$ 100,00: sem desconto ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (0.0, 0.0),
        (0.01, 0.01),
        (50.0, 50.0),
        (99.0, 99.0),
        (99.99, 99.99),
    ],
)
def test_pedidos_abaixo_de_100_nao_recebem_desconto(total, esperado):
    assert calcular_desconto(total) == esperado


# --- Limite: exatamente R$ 100,00 já recebe desconto ---

def test_pedido_exatamente_100_recebe_desconto_de_10_por_cento():
    assert calcular_desconto(100.0) == 90.0


def test_pedido_100_como_inteiro_recebe_desconto():
    assert calcular_desconto(100) == 90.0


def test_pedido_imediatamente_acima_do_limite_recebe_desconto():
    assert calcular_desconto(100.01) == 90.01


def test_pedido_imediatamente_abaixo_do_limite_nao_recebe_desconto():
    assert calcular_desconto(99.99) == 99.99


# --- Pedidos acima de R$ 100,00: 10% de desconto ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (150.0, 135.0),
        (200.0, 180.0),
        (250.5, 225.45),
        (1000.0, 900.0),
        (12345.6, 11111.04),
    ],
)
def test_pedidos_a_partir_de_100_recebem_desconto_de_10_por_cento(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


# --- Arredondamento para 2 casas decimais ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),    # 90.009  -> 90.01
        (133.33, 120.0),    # 119.997 -> 120.00
        (111.11, 100.0),    # 99.999  -> 100.00
        (123.44, 111.1),    # 111.096 -> 111.10
        (101.23, 91.11),    # 91.107  -> 91.11
        (199.99, 179.99),   # 179.991 -> 179.99
    ],
)
def test_valor_final_com_desconto_e_arredondado_para_2_casas(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


@pytest.mark.parametrize("total", [100.01, 133.33, 101.23, 199.99, 250.5, 12345.6])
def test_resultado_com_desconto_nao_possui_mais_de_2_casas_decimais(total):
    resultado = calcular_desconto(total)
    assert round(resultado, 2) == resultado


@pytest.mark.parametrize("total", [0.01, 50.0, 99.99])
def test_resultado_sem_desconto_nao_possui_mais_de_2_casas_decimais(total):
    resultado = calcular_desconto(total)
    assert round(resultado, 2) == resultado


# --- Propriedades gerais ---

@pytest.mark.parametrize("total", [100.0, 100.01, 150.0, 500.0, 9999.99])
def test_valor_com_desconto_e_menor_que_o_total(total):
    assert calcular_desconto(total) < total


@pytest.mark.parametrize("total", [0.0, 10.0, 99.99])
def test_valor_sem_desconto_e_igual_ao_total(total):
    assert calcular_desconto(total) == total


def test_retorna_valor_numerico():
    assert isinstance(calcular_desconto(150.0), (int, float))
