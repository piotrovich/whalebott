import time
import requests
import telebot
import const


r = requests.get(const.ticker_surbtc, verify=False)
spread = str(int(float((r.json()['ticker']['min_ask'][0]))) - int(float((r.json()['ticker']['max_bid'][0]))))
def ejecuta():
	r = requests.get(const.ticker_surbtc, verify=False)
	spread = str(int(float((r.json()['ticker']['min_ask'][0]))) - int(float((r.json()['ticker']['max_bid'][0]))))
	tb = telebot.TeleBot(const.TOKEN) 
	time.sleep(10)

	if r.status_code == 200:
		from pprint import pprint
		if int(float(spread)) < 300000:
			print('***************************************************')
			pprint("Venta: "+ str((r.json()['ticker']['min_ask'][0])))
			pprint("UNA MIERDA DE SPREAD: "+ spread)
			pprint("Compra: "+ str((r.json()['ticker']['max_bid'][0])))
			pprint ('Hora: '+(str(time.strftime("%H:%M:%S"))))
			print('***************************************************')

			#tb.send_message(const.chatid, "UNA MIERDA DE SPREAD: "+ spread) 

		if int(float(spread)) > 300000:
			print('***************************************************')
			pprint("Venta: "+ str((r.json()['ticker']['min_ask'][0])))
			pprint("TRADING TIME!! "+ spread)
			pprint("Compra: "+ str((r.json()['ticker']['max_bid'][0])))
			pprint ('Hora: '+(str(time.strftime("%H:%M:%S"))))
			print('***************************************************')
			tb.send_message(const.chatid, "TRADING TIME!! "+ spread) 
	else:
		tb.send_message(const.chatid,"error codigo: "+str(r.status_code))
		print(r.status_code)

while True:
	try:
		ejecuta()
	except Exception:
		tb = telebot.TeleBot(const.TOKEN) 
		tb.send_message(const.chatid, 'Ocurrio un Error Inesperado')
		print('Ocurrio un Error Inesperado')
		continue