from __future__ import print_function
from time import time
import logging
from operator import itemgetter
from pymongo import MongoClient
import pandas as pd
import numpy as np
import prop

logger = logging.getLogger(__name__)


def rsi(df, window, targetcol='weightedAverage', colname='rsi'):
    """ Calculates the Relative Strength Index (RSI) from a pandas dataframe
    http://stackoverflow.com/a/32346692/3389859
    """
    series = df[targetcol]
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    # first value is sum of avg gains
    u[u.index[window - 1]] = np.mean(u[:window])
    u = u.drop(u.index[:(window - 1)])
    # first value is sum of avg losses
    d[d.index[window - 1]] = np.mean(d[:window])
    d = d.drop(d.index[:(window - 1)])
    rs = u.ewm(com=window - 1,
               ignore_na=False,
               min_periods=0,
               adjust=False).mean() / d.ewm(com=window - 1,
                                            ignore_na=False,
                                            min_periods=0,
                                            adjust=False).mean()
    df[colname] = 100 - 100 / (1 + rs)
    return df


def sma(df, smaperiod, targetcol='close', colname='sma'):
    """ Calculates Simple Moving Average on a 'targetcol' in a pandas dataframe
    """
    df[colname] = df[targetcol].rolling(min_periods=1, window=smaperiod, center=False).mean()
    # smavalues = df[targetcol].rolling(window=smaperiod).mean()
    # smavalues2 = df['close'].rolling(window=smaperiod).mean()
    # smavalues3 = df[targetcol].rolling(window=50).mean()
    # smavalues4 = df['close'].rolling(window=50).mean()

    # print('smavalues: ', smavalues)
    # print('smavalues2: ', smavalues2)
    # print('smavalues3: ', smavalues3)
    # print('smavalues4: ', smavalues4)
    # df[colname] = smavalues
    # print('dftail 30 sma: ',df.tail(30)[['sma']])
    return df


def ema(df, window, colname, targetcol='close', **kwargs):
    """ Calculates Expodential Moving Average on a 'targetcol' in a pandas
    dataframe """
    # targetcol='weightedAverage'
    df[colname] = df[targetcol].ewm(
        span=window,
        min_periods=kwargs.get('min_periods', 1),
        adjust=kwargs.get('adjust', True),
        ignore_na=kwargs.get('ignore_na', False)
    ).mean()
    return df


def macd(df, fastcol='emafast', slowcol='emaslow', colname='macd'):
    """ Calculates the differance between 'fastcol' and 'slowcol' in a pandas
    dataframe """
    df[colname] = df[fastcol] - df[slowcol]
    return df


def bbands(df, smaperiod, valorVela, targetcol='close', stddev=2.0):
    """ Calculates Bollinger Bands for 'targetcol' of a pandas dataframe """
    if not 'sma' in df:
        df = sma(df, smaperiod, targetcol)
    df['bbtop'] = df['sma'] + (stddev * df[targetcol].rolling(
        min_periods=smaperiod,
        window=smaperiod,
        center=False).std())
    df['bbbottom'] = df['sma'] - (stddev * df[targetcol].rolling(
        min_periods=smaperiod,
        window=smaperiod,
        center=False).std())
    df['bbrange'] = df['bbtop'] - df['bbbottom']
    df['bbpercent'] = ((df[targetcol] - df['bbbottom']) / df['bbrange']) - 0.5
    return df


def bollinger_strat(df, valorVela, targetcol='close'):
    # valor -1 es para vender, valor 1 es para comprar
    # for row in range(len(df)):
    # senal=0
    print('entrando a metodo bollinger_strat')
    print('valor df targetcool: ', df[targetcol].iloc[valorVela])
    # if (df[targetcol].iloc[valorvela] > df['bbtop'].iloc[valorvela]) and (df[targetcol].iloc[valorvela - 1] < df['bbtop'].iloc[valorvela - 1]):
    if (df[targetcol].iloc[valorVela] > df['sma'].iloc[valorVela]) and (
            df[targetcol].iloc[valorVela - 1] < df['sma'].iloc[valorVela - 1]):
        senal = -1
        print('valor -1!, vender!')

    # elif (df[targetcol].iloc[valorvela] < df['bbbottom'].iloc[valorvela]) and (df[targetcol].iloc[valorvela - 1] > df['bbbottom'].iloc[valorvela - 1]):
    elif (df[targetcol].iloc[valorVela] < df['sma'].iloc[valorVela]) and (
            df[targetcol].iloc[valorVela - 1] > df['sma'].iloc[valorVela - 1]):
        senal = 1
        print('valor +1, comprar')
    else:
        senal = 0
        print('valor 0, no hacer nada')

    print('saliendo metodo bollinger_strat')
    return senal


# COMPRAR
# currencyPair (Ej: 'ETH_ZEC'): En el mercado de de ETH se esta comprando ZEC.
# rate (Ej: 0.01): A que precio se quiere comprar ZEC.
# amount (Ej: 0.672956): Cantidad de ETH que se quiere gastar.
def comprar(df, polo, targetcol='close'):
    valorvela = df[targetcol].size - 1
    precioCompra = df[targetcol].iloc[valorvela]
    # cambiar montos
    comprar = polo.buy('USDT_ETH', precioCompra, 0.001)


# Igual que vender, son los mismos parametros
def vender(df, polo, targetcol='close'):
    valorvela = df[targetcol].size - 1
    precioVenta = df[targetcol].iloc[valorvela]
    # cambiar montos
    vender = polo.sell('USDT_ETH', precioVenta, 0.001)


# amount = es el que sera definido en la orden de compra
# Stop = rate del precio de compra
# Limit = variable relacionado al LAST
def stopLimit(df, amount, stop, limit, valorVela, ordenes, targetcol='close'):
    # sell
    # if amount < 0 and stop >= tick['highestbid']:
    if not ordenes:
        print('No existen ordenes en Stop/Limit')
    elif df[targetcol].iloc[valorVela] < stop:
        # sell amount at limit
        order = api.sell(limit, amount)
    #elif

    return order


def returnOpenOrders(polo):
    # Revisa si existe orden de compra
    try:
        order = polo.returnOpenOrders('USDT_BTC')
    except:
        order = False
    return order


def calcularStop(ordenes):
    print('asdas')


class Chart(object):
    """ Saves and retrieves chart data to/from mongodb. It saves the chart
    based on candle size, and when called, it will automaticly update chart
    data if needed using the timestamp of the newest candle to determine how
    much data needs to be updated """

    def __init__(self, api, pair, **kwargs):
        """
        api = poloniex api object
        pair = market pair
        period = time period of candles (default: 5 Min)
        """
        self.accion = False
        #definir bien!
        self.porcentajeStop = 0.0024
        self.pair = pair
        self.api = api
        self.period = kwargs.get('period', self.api.MINUTE * 5)
        self.db = MongoClient()['poloniex']['%s_%s_chart' %
                                            (self.pair, str(self.period))]

    def __call__(self, size=0):
        """ Returns raw data from the db, updates the db if needed """
        # get old data from db
        try:
            # get last candle
            old = sorted(list(self.db.find().skip(self.db.find().count() - 288)), key=itemgetter('_id'))
            last = old[-1]
        except:
            # no candle found, db collection is empty
            last = False
        # no entrys found, get last year of data to fill the db
        if not last:
            logger.warning('%s collection is empty!',
                           '%s_%s_chart' % (self.pair, str(self.period)))
            # new = self.api.returnChartData(self.pair,
            #                               period=self.period,
            #                               start=time() - self.api.YEAR)
            new = self.api.returnChartData(self.pair,
                                           period=self.period,
                                           start=time() - self.api.DAY)
        # we have data in db already
        else:
            new = self.api.returnChartData(self.pair,
                                           period=self.period,
                                           start=int(last['_id']))
        # add new candles
        updateSize = len(new)
        logger.info('Updating %s with %s new entrys!',
                    self.pair + '-' + str(self.period), str(updateSize))
        # show progress
        for i in range(updateSize):
            print("\r%s/%s" % (str(i + 1), str(updateSize)), end=" complete ")
            date = new[i]['date']
            del new[i]['date']
            self.db.update_one({'_id': date}, {"$set": new[i]}, upsert=True)
        print('')
        logger.debug('Getting chart data from db')
        # return data from db
        return sorted(list(self.db.find()), key=itemgetter('_id'))[-size:]

    def dataFrame(self, size=0, window=120):
        # get data from db
        data = self.__call__(size)
        # make dataframe
        df = pd.DataFrame(data)
        # format dates
        df['date'] = [pd.to_datetime(c['_id'], unit='s') for c in data]
        # del '_id'
        del df['_id']
        # set 'date' col as index
        df.set_index('date', inplace=True)
        if not self.polo:
            self.polo = Poloniex(prop.apikey, prop.apiSecret)
        # Variables SMA, EMA, RSI valorvela
        smaperiod = 50
        ema20 = 20
        ema30 = 30
        self.valorVela = df['close'].size - 1
        # calculate/add sma and bbands
        df = bbands(df, smaperiod, self.valorVela)


        # add slow ema
        #df = ema(df, ema30, colname='emaslow')
        # add fast ema
        #df = ema(df, ema20, colname='emafast')
        # add macd
        # df = macd(df)
        # add rsi
        # df = rsi(df, window // 5)
        # add candle body and shadow size
        # df['bodysize'] = df['open'] - df['close']
        # df['shadowsize'] = df['high'] - df['low']
        # add percent change
        df['percentChange'] = df['close'].pct_change()
        return df

    def botWhale(self, df):
        senal = bollinger_strat(df, self.valorVela)

        # metodo buy
        if senal == 1:
            comprar(df, self.polo)
            self.ordenes = True
            self.enProceso = 'compra'
        # metodo sell
        elif senal < 0:
            vender(df, self.polo)
            self.enProceso = 'venta'

        # metodo Stop

        if self.ordenes:
            self.ordenes = returnOpenOrders(self.polo)
            if self.enProceso == 'compra':
                self.stop = calcularStop(self.ordenes)

        if self.ordenes:
            order = stopLimit(df, amount, stop, limit, valorVela, ordenes)

    def ejecuta(self):
        print('entre al ejecuta')
        try:
            while True:
                df=self.dataFrame()
                self.botWhale(df)
        except:
            print('error!, vuelve a ejecutar!')
            self.ejecuta()


if __name__ == '__main__':
    from poloniex import Poloniex

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("poloniex").setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.ERROR)
    api = Poloniex(jsonNums=float)
    #df = Chart(api, 'USDT_BTC').dataFrame()
    Chart(api, 'USDT_BTC').ejecuta()
    # print(df.tail(7)[['open', 'close', 'percentChange', 'sma','emaslow', 'emafast', 'macd', 'bbtop', 'bbbottom', 'bbrange', 'bbpercent']])
    #print('df tail: ', df.tail(60)[['close', 'sma', 'bbtop', 'bbbottom']])
    #tail = df.tail(51)['close']
    #print('trail size: ', df.tail(51)['sma'].size)
    #print('trail size2: ', df['sma'].size)
    #print('trail size3: ', df['sma'].size - 1)
    #tail2 = df.tail(120)['close']

#    valoressma = ""
#    for i in range(tail2.size):
 #       valoressma += str(tail2.values[i]) + ','
 #   print('----------------------')
 #   print('valoressma: ', valoressma)
 #   qwe = 0
# for i in range(50):
# print('valor i: ', i, ', valor tail: ', tail.values[i])
# qwe= qwe + tail2.values[i]
