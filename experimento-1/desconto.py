def calcular_desconto(total):
    """Calcula o valor final do pedido com desconto."""
    if total > 100:
        return round(total * 0.9, 2)
    return total
