import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (0, 0),
        (50, 50),
        (99.99, 99.99),
    ],
)
def test_pedido_abaixo_de_100_nao_recebe_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


def test_pedido_exatamente_100_recebe_desconto_de_10_por_cento():
    assert calcular_desconto(100) == pytest.approx(90.00)


def test_pedido_exatamente_100_00_float_recebe_desconto():
    assert calcular_desconto(100.00) == pytest.approx(90.00)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (150, 135.00),
        (200, 180.00),
        (1000, 900.00),
    ],
)
def test_pedido_acima_de_100_recebe_desconto_de_10_por_cento(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (199.99, 179.99),
        (111.11, 100.00),
        (100.01, 90.01),
    ],
)
def test_valor_final_com_desconto_arredondado_para_2_casas(total, esperado):
    resultado = calcular_desconto(total)
    assert resultado == round(resultado, 2)
    assert resultado == pytest.approx(esperado)


def test_limite_entre_sem_desconto_e_com_desconto():
    assert calcular_desconto(99.99) == pytest.approx(99.99)
    assert calcular_desconto(100) == pytest.approx(90.00)
