import poloniex
import prop

polo = poloniex.Poloniex(prop.apikey,prop.apiSecret)
try:
    currencyPair = 'USDT_BTC'
    valor_vela = float("{0:.8f}".format(10000))
    monto = float("{0:.8f}".format(3.91909389))

    #monto = float("{0:.8f}".format(0.00866030))
    #valor_monto = float("{0:.8f}".format(((monto * 100) / valor_vela) / 100))
    valor_monto_str =str(((monto * 100) / valor_vela) / 100)
    valor_list = valor_monto_str.split('.')
    if len(valor_list[1]) > 8:
        valor_float= float(valor_list[0] +'.'+ valor_list[1][0:8])

    else:
        valor_float = float(valor_monto_str)



    roo = polo.returnOpenOrders('USDT_BTC')
    #number = int(roo[0]['orderNumber'])

    #move = polo.moveOrder(number, 8300)
    #new_number = move['orderNumber']
    number = 171426315208
    cancel = polo.cancelOrder(number)

    print('listo')
    """
    COMPRA!
    
    return_fee = polo.returnFeeInfo()
    print('retorno de FEE: ', return_fee)
    valor_monto = ((monto * 100) / valor_vela) / 100
    comprar = polo.buy(currencyPair, valor_vela, float("{0:.8f}".format(valor_monto)))
    order_number=comprar['orderNumber']
    print('comprar: ', comprar)
    #cancel = polo.cancelOrder(int(order_number))
    return_fee = polo.returnFeeInfo()
    print('retorno de FEE: ', return_fee)
    
    """

    """
    VENTA!
    """
    currencyPair = 'USDT_BTC'
    valor_vela = float("{0:.8f}".format(7800))

    rcb = polo.returnCompleteBalances()
    monto = float(rcb['BTC']['available'])

    vender = polo.sell(currencyPair, valor_vela, monto)
    new_number2 = vender['orderNumber']
    print('vender: ', vender)
    return_fee = polo.returnFeeInfo()
    print('retorno de FEE: ', return_fee)


except Exception as err:
    print('ERROR!: ', str(err))


