import time
import prop
import requests
import poloniex

tiempo = int("{:.6f}".format(time.time()).replace('.', ''))
print('holaaa')
print(tiempo)


polo = poloniex.Poloniex(prop.apikey,prop.apiSecret)
try:
    """
    polo.buy()
except:
    ordenes = False
    print('fallo la wea')
    """



    ordenes = True
    if ordenes:
        print('si hay!')
    ordenes = polo.returnOpenOrders('USDT_BTC')
    print('ordenes 1: ', ordenes)
    ordenes2 = polo.returnOpenOrders('ETH_BCH')
    print('ordenes 2: ', ordenes2)
    if ordenes:
        print('si hay!')
    ordenes = []
    ordenes.append({'orderNumber': '166655017999', 'type': 'sell', 'rate': '2000.00000000', 'startingAmount': '0.00300000', 'amount': '0.00300000', 'total': '6.00000000', 'date': '2018-02-22 16:17:42', 'margin': 0})
    ordenes.append(
        {'orderNumber': '166655017923', 'type': 'sell', 'rate': '2000.00000000', 'startingAmount': '0.00300000',
         'amount': '0.00500000', 'total': '6.00000000', 'date': '2018-02-22 16:17:42', 'margin': 0})

    monto_total = 0
    for ord in ordenes:
        monto_total += float(ord['amount'])


    for ord in ordenes:
        if '166655017999' == ord['orderNumber']:
            ordenes.remove(ord)
            print('hola')
            print('ordenes: ', ordenes)

    returnTradeHistory = False

    while not returnTradeHistory:
        returnTradeHistory = polo.returnTradeHistory('USDT_BTC', time.time() - polo.WEEK)
        if returnTradeHistory:
            print('while en TRUE!')
            fecha = returnTradeHistory[0]['date']
            print('returnTradeHistory: ', returnTradeHistory)
            print('dato que me sirve: ', returnTradeHistory[0]['rate'], ', ', returnTradeHistory[0]['orderNumber'])
            for ord in returnTradeHistory:
                if ord['type'] == 'buy':
                    print('este es tipo buy: ', ord)
                    break
        else:
            print('While en false')

    balanceCom = polo.returnCompleteBalances()
    currencyPair = 'BTC'
    print(float(balanceCom[currencyPair]['available']) > 0)

    balance = polo.returnBalances()
    print('todas las ordenes: ', ordenes)
    print('ordenes 1: ', ordenes[0])
    print('ordenes 2: ', ordenes[0]['orderNumber'])
#    print('ordenes 3: ', ordenes[0][0])
    #print('tamaño: ', len(ordenes))
    print('balance completo: ', balanceCom)
    print('balance completo ETH: ', balanceCom['ETH'])
    print('balance completo USDT: ', balanceCom['USDT'])
    valor1 = float(balanceCom['USDT']['available'])
    valor2 = float(balanceCom['ETH']['available'])
    valor3 = valor1+valor2
    print('valor3: ', valor3)
    print('balance completo USDT: ', balanceCom['USDT']['available'])
    print('balance completo ETH: ', balanceCom['ETH']['available'])
    print('balance completo BTC: ', balanceCom['BTC']['available'])
    return_fee = polo.returnFeeInfo()
    print('retorno de FEE: ', return_fee)
    returnTrade_History = polo.returnTradeHistory('USDT_BTC')
    print('returnTradeHistory: ', returnTrade_History)
    if float(balanceCom['BTC']['available']) > 0:
        print('si hay btc')
    else:
        print('no hay btc')
    print('balance normal: ', balance)
    asd= 'ETH'
    print('balance ETH: ', balance[asd])
   # for i in ordenes:
    #    order=i['amount']
     #   print('')
except Exception as err:
    ordenes = False
    print('fallo la wea, ', str(err))

if ordenes:
    print('existen ordenes')
else:
    print('no existen ordenes')
#USDT_ETH
#print('order: ', order)
#print('ordenes: ', ordenes)



