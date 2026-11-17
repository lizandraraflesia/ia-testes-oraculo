import pytest

from desconto import calcular_desconto


@pytest.mark.parametrize(
    "total, esperado",
    [
        (0, 0),
        (50, 50),
        (99.99, 99.99),
        (100, 100),
    ],
)
def test_sem_desconto_ate_100(total, esperado):
    assert calcular_desconto(total) == esperado


@pytest.mark.parametrize(
    "total, esperado",
    [
        (100.01, 90.01),
        (101, 90.9),
        (150, 135.0),
        (200, 180.0),
        (1000, 900.0),
    ],
)
def test_desconto_de_10_por_cento_acima_de_100(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado)


def test_limite_exato_100_nao_recebe_desconto():
    assert calcular_desconto(100) == 100


def test_valor_logo_acima_do_limite_recebe_desconto():
    assert calcular_desconto(100.01) < 100.01


def test_resultado_com_desconto_arredondado_para_duas_casas():
    resultado = calcular_desconto(123.45)
    assert resultado == round(resultado, 2)
    assert resultado == pytest.approx(111.11)


def test_valor_sem_desconto_retornado_inalterado():
    total = 42.123
    assert calcular_desconto(total) == total


def test_retorna_mesmo_objeto_quando_sem_desconto():
    total = 80
    assert calcular_desconto(total) is total


def test_total_negativo_retornado_inalterado():
    assert calcular_desconto(-10) == -10


def test_aceita_inteiro_e_float_com_mesmo_resultado():
    assert calcular_desconto(200) == pytest.approx(calcular_desconto(200.0))


def test_tipo_invalido_lanca_type_error():
    with pytest.raises(TypeError):
        calcular_desconto("150")


def test_none_lanca_type_error():
    with pytest.raises(TypeError):
        calcular_desconto(None)
