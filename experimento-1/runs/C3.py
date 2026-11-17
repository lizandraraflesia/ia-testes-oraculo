import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (0.01, 0.01),
        (50.00, 50.00),
        (99.98, 99.98),
        (99.99, 99.99),
    ],
)
def test_pedidos_abaixo_de_100_nao_recebem_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


def test_pedido_exatamente_100_recebe_desconto():
    assert calcular_desconto(100.00) == pytest.approx(90.00, abs=1e-9)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (150.00, 135.00),
        (200.00, 180.00),
        (1000.00, 900.00),
        (12345.60, 11111.04),
    ],
)
def test_pedidos_a_partir_de_100_recebem_10_por_cento_de_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (199.99, 179.99),
        (333.33, 300.00),
        (111.11, 100.00),
        (123.43, 111.09),
    ],
)
def test_valor_final_arredondado_para_duas_casas(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


@pytest.mark.parametrize(
    "total",
    [0.01, 99.99, 100.00, 100.01, 123.43, 199.99, 333.33, 777.77, 12345.67],
)
def test_resultado_tem_no_maximo_duas_casas_decimais(total):
    resultado = calcular_desconto(total)
    assert float(resultado) == pytest.approx(round(float(resultado), 2), abs=1e-9)


def test_desconto_nao_torna_pedido_acima_do_limite_mais_caro_que_abaixo():
    assert calcular_desconto(100.00) < calcular_desconto(99.99)


@pytest.mark.parametrize("total", [100.00, 150.00, 500.00, 9999.99])
def test_valor_com_desconto_e_menor_que_total(total):
    assert calcular_desconto(total) < total


@pytest.mark.parametrize("total", [0.01, 10.00, 99.99])
def test_valor_sem_desconto_e_igual_ao_total(total):
    assert calcular_desconto(total) == pytest.approx(total, abs=1e-9)
