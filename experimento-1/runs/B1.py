import pytest

from desconto import calcular_desconto


# Requisito: pedidos a partir de R$ 100,00 (inclusive) recebem 10% de desconto.
# Observação: a implementação atual usa "total > 100", então o teste do
# limite exato (R$ 100,00) deve falhar até a condição virar "total >= 100".


@pytest.mark.parametrize(
    "total, esperado",
    [
        (0, 0),
        (0.01, 0.01),
        (50, 50),
        (99.99, 99.99),
    ],
)
def test_pedidos_abaixo_de_100_nao_recebem_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


def test_pedido_de_exatamente_100_recebe_desconto():
    assert calcular_desconto(100) == pytest.approx(90.00)


def test_pedido_de_exatamente_100_com_decimais_recebe_desconto():
    assert calcular_desconto(100.00) == pytest.approx(90.00)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (150, 135.00),
        (200, 180.00),
        (1000, 900.00),
        (12345.67, 11111.10),
    ],
)
def test_pedidos_acima_de_100_recebem_10_porcento_de_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),    # 90.009  -> 90.01
        (199.99, 179.99),   # 179.991 -> 179.99
        (123.45, 111.11),   # 111.105 -> 111.11 (ou 111.10, conforme float)
        (111.11, 100.00),   # 99.999  -> 100.00
    ],
)
def test_valor_com_desconto_e_arredondado_para_duas_casas(total, esperado):
    resultado = calcular_desconto(total)
    assert resultado == pytest.approx(esperado, abs=0.01)
    assert round(resultado, 2) == resultado


def test_resultado_com_desconto_tem_no_maximo_duas_casas_decimais():
    resultado = calcular_desconto(333.33)
    assert resultado == round(resultado, 2)
    assert resultado == pytest.approx(300.00)


def test_valor_com_desconto_e_menor_que_o_total():
    total = 250
    assert calcular_desconto(total) < total


def test_valor_sem_desconto_e_igual_ao_total():
    total = 42.5
    assert calcular_desconto(total) == total
