import poloniex
import prop

def calcularFloat(valor):
    """
        Metodo que toma los ultimos 8 digitos SIN REDONDEAR
    :param valor: valor que se quiere operar
    :return: valor calculado
    """
    valor_str = str(valor)
    valor_list = valor_str.split('.')
    if len(valor_list[1]) > 8:
        valor = float(valor_list[0] + '.' + valor_list[1][0:8])
        return valor
    else:
        return float(valor)


def calcular_monto(monto_usdt, precio_compra):
    """
        Metodo que calcula monto a comprar en la criptomoneda deseada
    :param monto_usdt: Monto de dolares a comprar
    :param precio_compra: precio al que se quiere comprar
    :return: valor_monto
    """
    valor_monto = calcularFloat(((monto_usdt * 100) / precio_compra) / 100)
    return valor_monto


polo = poloniex.Poloniex(prop.apikey,prop.apiSecret)
try:
    currencyPair = 'USDT_BTC'
    valor_vela = float("{0:.8f}".format(9000))
    monto = float("{0:.8f}".format(2.98135780))

    #monto = float("{0:.8f}".format(0.00866030))
    #valor_monto = float("{0:.8f}".format(((monto * 100) / valor_vela) / 100))
    valor_monto_str =str(((monto * 100) / valor_vela) / 100)
    valor_list = valor_monto_str.split('.')
    if len(valor_list[1]) > 8:
        valor_float= float(valor_list[0] +'.'+ valor_list[1][0:8])

    else:
        valor_float = float(valor_monto_str)


    #MOVE!
    roo = polo.returnOpenOrders('USDT_BTC')
    number = int(roo[0]['orderNumber'])
    nuevo_precio_compra =9000
    monto_usdt_nuevo = calcularFloat(float(roo[0]['amount']) * nuevo_precio_compra)
    #monto_usdt_nuevo = calcularFloat(nuevo_precio_compra * valor_monto_nuevo)
    rcb = polo.returnCompleteBalances()
    suma_usdt = float(rcb['USDT']['available']) + float(rcb['USDT']['onOrders'])

    if suma_usdt >= monto_usdt_nuevo:
        move = polo.moveOrder(number, nuevo_precio_compra)
    else:
        valor_monto_nuevo = calcular_monto(suma_usdt, nuevo_precio_compra)
        move = polo.moveOrder(number, nuevo_precio_compra, valor_monto_nuevo)
    print('mover!: ', str(move))
    print('rescatar valores que quiero: ', move['resultingTrades']['USDT_BTC'])
    if move['resultingTrades']['USDT_BTC']:
        print('wena')
        print('amount: ', move['resultingTrades']['USDT_BTC'][0]['amount'])
    else:
        print('mala')
    #new_number = move['orderNumber']

    """
    #CANCEL!
    roo = polo.returnOpenOrders('USDT_BTC')
    number = int(roo[0]['orderNumber'])
    cancel = polo.cancelOrder(number)
    print('cancel: ', str(cancel))
    
    
    
    #COMPRA!
    valor_vela = float("{0:.8f}".format(6000))
    rcb = polo.returnCompleteBalances()
    monto = float(rcb['USDT']['available'])
    valor_monto = calcularFloat(((monto * 100) / valor_vela) / 100)
    print('monto: ', monto, ', valor_monto: ', valor_monto)
    comprar = polo.buy(currencyPair, valor_vela, float("{0:.8f}".format(valor_monto)))
    order_number=comprar['orderNumber']
    print('comprar: ', comprar)
    #cancel = polo.cancelOrder(int(order_number))
    return_fee = polo.returnFeeInfo()
    print('retorno de FEE: ', return_fee)

    


    
    #VENTA!

    currencyPair = 'USDT_BTC'
    valor_vela = float("{0:.8f}".format(6000))

    rcb = polo.returnCompleteBalances()
    monto = float(rcb['BTC']['available'])

    vender = polo.sell(currencyPair, valor_vela, monto)
    new_number2 = vender['orderNumber']
    print('vender: ', vender)
    """


except Exception as err:
    print('ERROR!: ', str(err))


