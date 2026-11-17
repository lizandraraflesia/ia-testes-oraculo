import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (0, 0),
        (50.00, 50.00),
        (99.99, 99.99),
    ],
)
def test_pedido_abaixo_de_100_nao_recebe_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


def test_pedido_exatamente_100_recebe_desconto():
    # Requisito: "a partir de R$ 100,00" inclui o próprio valor de 100,00
    assert calcular_desconto(100.00) == pytest.approx(90.00)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (150.00, 135.00),
        (200.00, 180.00),
        (1000.00, 900.00),
    ],
)
def test_pedido_acima_de_100_recebe_10_por_cento_de_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


@pytest.mark.parametrize("total", [100.00, 100.01, 133.33, 250.75, 999.99])
def test_valor_com_desconto_tem_no_maximo_duas_casas_decimais(total):
    resultado = calcular_desconto(total)
    assert resultado == round(resultado, 2)


def test_arredondamento_do_valor_com_desconto():
    # 100.01 * 0.9 = 90.009 -> 90.01
    assert calcular_desconto(100.01) == 90.01
