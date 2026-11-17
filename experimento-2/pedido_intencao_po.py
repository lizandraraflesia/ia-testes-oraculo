# Intenção do negócio (definida pelo PO, não escrita no requisito):
# - a faixa de R$ 200 considera o subtotal ANTES do cupom;
# - desconto de faixa e VIP NÃO acumulam: vale o maior;
# - o cupom é abatido DEPOIS dos descontos percentuais;
# - o total nunca fica negativo.
def calcular_total(subtotal, vip=False, cupom=0.0):
    pct = 0.0
    if subtotal >= 200:
        pct = 0.10
    if vip:
        pct = max(pct, 0.05)
    valor = subtotal * (1 - pct) - cupom
    return round(max(valor, 0), 2)
