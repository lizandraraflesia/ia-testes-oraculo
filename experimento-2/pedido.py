def calcular_total(subtotal, vip=False, cupom=0.0):
    """Calcula o valor final do pedido."""
    valor = subtotal - cupom
    desconto = 0.0
    if valor >= 200:
        desconto += 0.10
    if vip:
        desconto += 0.05
    return round(valor * (1 - desconto), 2)
