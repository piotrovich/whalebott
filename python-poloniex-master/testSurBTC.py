from surbtc import SURBTC
client = SURBTC.Public()
jsonBTC=client.ticker("BTC_CLP")
ticker_btc = client.ticker('BTC_CLP')[0][1]
print(str(ticker_btc))
print(jsonBTC)