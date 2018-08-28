import requests
import poloniex
#import time
from time import time
import prop

r = requests.get('https://poloniex.com/public?command=returnTradeHistory&currencyPair=USDT_BTC')


def promediarlistaBuy(listaBuy):
    sum = 0.0
    for i in range(0, len(listaBuy)):
        sum += listaBuy[i]

    return sum / len(listaBuy)


def imprimirlistaBuy(listaBuy, nombre):
    for i in range(0, len(listaBuy)):
        if r.json()[i]['type'] == 'buy':
            print(nombre + " buy" + ": $" + str(listaBuy[i]))
        # "[" + str(i) + "]=" para ver la posicion de la compra


def leerlistaBuy():
    listaBuy = []
    i = 0
    while i < 200:
        listaBuy.append(int(float(r.json()[i]['total'])))
        i += 1
    return listaBuy

#print('r json: ', r.json())
A = leerlistaBuy()
imprimirlistaBuy(A, "USDT")
print("Promedio de Compra = " + "$" + str(promediarlistaBuy(A)))
#print('Hora: ' + (str(time.strftime("%H:%M:%S"))))
print('')

##############################################################################
"""
def promediarListaSell(listaSell):
	sum = 0.0
	for i in range(0,len(listaSell)):
		sum += listaSell[i]
	return sum/len(listaSell)

def imprimirlistaSell(listaSell,nombre):
	for i in range(0,len(listaSell)):
		if r.json()[i]['type'] == 'sell':
			print(nombre + " sell" + ": $" + str(listaSell[i]))
				#"[" + str(i) + "]=" para ver la posicion de la venta

def leerlistaSell():
	listaSell = []
	i = 0
	while i < 200:
			listaSell.append(int(float(r.json()[i]['total'])))
			i += 1
	return listaSell

B = leerlistaSell()
imprimirlistaSell(B, "USDT")
print("Promedio de Venta = " + "$" +str(promediarListaSell(B))) 
print('Hora: '+(str(time.strftime("%H:%M:%S"))))
print('')
"""
################################################################
def promedioBuy(order):
    sum = 0.0
    contador = 0
    for ord in order:
        if ord['type'] == 'buy' and contador <= 200:
            sum += float(ord['total'])
            contador +=1

    sum = sum / 200
    return sum


#currencyPair = 'USDT_BTC'
currencyPair = 'USDT_ETC'
api = poloniex.Poloniex(jsonNums=float)
order = api.marketTradeHist(currencyPair, time() - api.HOUR)
print('returnTradeHistory: ', order)
print('return tamaño: ', len(order))
sum = promedioBuy(order)
print('promedio dolares: ', sum)

