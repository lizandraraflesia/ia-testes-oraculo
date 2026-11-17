import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (101, 90.9),
        (150, 135.0),
        (200, 180.0),
        (1000, 900.0),
        (100.5, 90.45),
        (100.01, 90.01),
    ],
)
def test_aplica_desconto_de_10_por_cento_acima_de_100(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


@pytest.mark.parametrize("total", [0, 1, 50, 99.99, 100])
def test_nao_aplica_desconto_ate_100(total):
    assert calcular_desconto(total) == total


def test_limite_exato_de_100_nao_recebe_desconto():
    assert calcular_desconto(100) == 100


def test_valor_logo_acima_do_limite_recebe_desconto():
    assert calcular_desconto(100.01) < 100.01


def test_resultado_com_desconto_tem_no_maximo_duas_casas_decimais():
    resultado = calcular_desconto(123.45)
    assert resultado == round(resultado, 2)
    assert resultado == pytest.approx(111.11)


def test_sem_desconto_retorna_o_mesmo_valor_sem_arredondar():
    assert calcular_desconto(99.999) == 99.999


def test_valor_negativo_retorna_o_proprio_valor():
    assert calcular_desconto(-50) == -50


def test_retorna_float_quando_ha_desconto():
    assert isinstance(calcular_desconto(200), float)


def test_retorna_tipo_original_quando_nao_ha_desconto():
    assert isinstance(calcular_desconto(50), int)


def test_entrada_invalida_lanca_type_error():
    with pytest.raises(TypeError):
        calcular_desconto("200")


def test_entrada_none_lanca_type_error():
    with pytest.raises(TypeError):
        calcular_desconto(None)
