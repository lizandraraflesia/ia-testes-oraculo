import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (101, 90.9),
        (150, 135.0),
        (199.99, 179.99),
        (1000, 900.0),
        (123.45, 111.11),
    ],
)
def test_aplica_desconto_de_10_por_cento_acima_de_100(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


@pytest.mark.parametrize(
    "total",
    [100, 100.0, 99.99, 50, 1, 0, 0.0],
)
def test_nao_aplica_desconto_ate_100(total):
    assert calcular_desconto(total) == total


def test_limite_exato_de_100_nao_tem_desconto():
    assert calcular_desconto(100) == 100


def test_valor_logo_acima_do_limite_tem_desconto():
    assert calcular_desconto(100.01) < 100.01


def test_resultado_com_desconto_tem_no_maximo_duas_casas_decimais():
    resultado = calcular_desconto(333.33)
    assert resultado == round(resultado, 2)
    assert resultado == pytest.approx(300.0)


def test_valor_sem_desconto_e_retornado_sem_arredondamento():
    assert calcular_desconto(50.555) == 50.555


def test_valor_negativo_e_retornado_sem_alteracao():
    assert calcular_desconto(-10) == -10


def test_preserva_tipo_inteiro_quando_nao_ha_desconto():
    resultado = calcular_desconto(80)
    assert resultado == 80
    assert isinstance(resultado, int)


def test_retorna_float_quando_ha_desconto():
    assert isinstance(calcular_desconto(200), float)


@pytest.mark.parametrize("entrada_invalida", ["200", None, [150]])
def test_entrada_invalida_levanta_type_error(entrada_invalida):
    with pytest.raises(TypeError):
        calcular_desconto(entrada_invalida)
