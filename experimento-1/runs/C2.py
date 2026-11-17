import pytest

from desconto import calcular_desconto


# --- Pedidos abaixo de R$ 100,00: sem desconto ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (0.00, 0.00),
        (0.01, 0.01),
        (50.00, 50.00),
        (99.98, 99.98),
        (99.99, 99.99),
    ],
)
def test_pedido_abaixo_de_100_nao_recebe_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


# --- Limite exato: R$ 100,00 já recebe desconto ("a partir de") ---

def test_pedido_exatamente_100_recebe_10_por_cento_de_desconto():
    assert calcular_desconto(100.00) == pytest.approx(90.00, abs=1e-9)


def test_pedido_logo_acima_do_limite_recebe_desconto():
    # 100.01 * 0.9 = 90.009 -> 90.01
    assert calcular_desconto(100.01) == pytest.approx(90.01, abs=1e-9)


# --- Pedidos acima de R$ 100,00: 10% de desconto ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (150.00, 135.00),
        (200.00, 180.00),
        (250.50, 225.45),
        (1000.00, 900.00),
        (1_000_000.00, 900_000.00),
    ],
)
def test_pedido_acima_de_100_recebe_10_por_cento_de_desconto(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


# --- Arredondamento para 2 casas decimais ---

@pytest.mark.parametrize(
    "total, esperado",
    [
        (199.99, 179.99),   # 179.991 -> 179.99 (arredonda para baixo)
        (133.33, 120.00),   # 119.997 -> 120.00 (arredonda para cima)
        (111.11, 100.00),   # 99.999  -> 100.00
        (123.47, 111.12),   # 111.123 -> 111.12
        (987.67, 888.90),   # 888.903 -> 888.90
    ],
)
def test_valor_final_e_arredondado_para_duas_casas(total, esperado):
    assert calcular_desconto(total) == pytest.approx(esperado, abs=1e-9)


@pytest.mark.parametrize(
    "total",
    [0.00, 10.00, 99.99, 100.00, 100.01, 123.47, 133.33, 199.99, 987.67, 12345.67],
)
def test_resultado_tem_no_maximo_duas_casas_decimais(total):
    resultado = calcular_desconto(total)
    assert resultado == pytest.approx(round(resultado, 2), abs=1e-9)


# --- Propriedades gerais ---

@pytest.mark.parametrize("total", [0.00, 1.00, 99.99, 100.00, 150.00, 5000.00])
def test_valor_final_nunca_e_maior_que_o_total(total):
    assert calcular_desconto(total) <= total + 1e-9


@pytest.mark.parametrize("total", [0.00, 1.00, 99.99, 100.00, 150.00, 5000.00])
def test_valor_final_nunca_e_negativo(total):
    assert calcular_desconto(total) >= 0


def test_resultado_e_numerico():
    assert isinstance(calcular_desconto(150.00), (int, float))


def test_aceita_total_inteiro():
    assert calcular_desconto(100) == pytest.approx(90.00, abs=1e-9)
    assert calcular_desconto(99) == pytest.approx(99.00, abs=1e-9)
