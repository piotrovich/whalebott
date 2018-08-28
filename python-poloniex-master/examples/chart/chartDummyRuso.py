from __future__ import print_function
from time import time
import logging
from operator import itemgetter
from pymongo import MongoClient
import pandas as pd
import numpy as np
import prop


def rsi(df, window, targetcol='close', colname='rsi'):
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
    return df


def ema(df, window, colname, targetcol='close', **kwargs):
    """ Calculates Expodential Moving Average on a 'targetcol' in a pandas
    dataframe """
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


def bbands(df, smaperiod, targetcol='close', stddev=2.0):
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


def comprar(polo, currencyPair, valor_vela, monto):
    """
        Metodo Comprar
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :param valor_vela: Valor actual de la vela (self.valorVela)
    :param monto: monto calculado que se comprara (float)
    :return: comprar
    """
    try:
        comprar = polo.buy(currencyPair, valor_vela, monto)
    except:
        comprar = False
    return comprar


def vender(polo, currencyPair, valor_vela, monto):
    """
        metodo vender
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :param valor_vela: Valor actual de la vela (self.valorVela)
    :param monto: monto calculado que se comprara (float)
    :return: vender
    """
    try:
        vender = polo.sell(currencyPair, valor_vela, monto)
    except:
        vender = False
    return vender


def moveOrder(polo, order_number, valor_vela, amount):
    """
        Metodo que mueve una orden sin necesidad de cancelarla antes
    :param polo: api Poloniex (self.polo)
    :param order_number: numero de orden a mover (compra, venta u ordenStop)
    :param valor_vela: Valor actual de la vela (self.valorVela)
    :param amount:  False = mueve la orden con el monto ya existente
                    True = mueve orden con nuevo monto calculado
    :return: order
    """
    try:
        if not amount:
            order = polo.moveOrder(order_number, valor_vela)
        else:
            order = polo.moveOrder(order_number, valor_vela, amount)
        if order['success'] != 1:
            order = False
    except:
        order = False
    return order


def returnOpenOrders(polo, currencyPair):
    """
        Metodo que retorna nuestras ordenes abiertas de un mercado especifico
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :return: order
    """
    # Revisa si existe orden de compra
    try:
        order = polo.returnOpenOrders(currencyPair)
    except:
        order = False
    return order


def returnCompleteBalances(polo):
    """
        Metodo que retorna los balances (disponible, en orden y calculado en BTC)
    :param polo: api Poloniex (self.polo)
    :return: order
    """
    # Devuelve todos sus saldos, incluido el saldo disponible, el saldo en pedidos y el valor estimado de BTC de su saldo
    try:
        order = polo.returnCompleteBalances()
    except:
        order = False
    return order


def returnBalances(polo):
    """
        Retorna todos los balances disponibles
    :param polo: api Poloniex (self.polo)
    :return: order
    """
    try:
        order = polo.returnBalances()
    except:
        order = False
    return order


def cancelOrder(polo, order_number):
    """
        Cancela una orden en especifico (con el numero de orden)
    :param polo: api Poloniex (self.polo)
    :param order_number: numero de orden a cancelar (compra, venta u ordenStop)
    :return: order
    """
    try:
        order = polo.cancelOrder(order_number)
        if order['success'] != 1:
            order = False
    except:
        order = False
    return order


def marketTradeHist(polo, currencyPair, start):
    """
        Retorna el mercado historico de un mercado en especifico en un tiempo designado
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :param start: Tiempo desde cuando se requiere el historico
    :return: order
    """
    try:
        order = polo.marketTradeHist(currencyPair, start)
    except:
        order = False
    return order


def procesarRCB(order, currencyPair):
    """
        Metodo que procesa returnCompleteBalances y responde:
            1 = si existen solo montos disponibles
            2 = si existen solo ordenes abiertas
            3 = si existen montos disponibles y ordenes abiertas
            0 = no existen montos disponibles u ordenes abiertas
    :param order: returnCompleteBalances (self.rcb)
    :param currencyPair: Moneda a consultar, ej: 'BTC'
    :return: tipo_rcb
    """
    if (float(order[currencyPair]['available']) > 0) and (float(order[currencyPair]['onOrders']) > 0):
        tipo_rcb = 3
    elif float(order[currencyPair]['available']) > 0:
        tipo_rcb = 1
    elif float(order[currencyPair]['onOrders']) > 0:
        tipo_rcb = 2
    elif (float(order[currencyPair]['available']) == 0) and (float(order[currencyPair]['onOrders']) == 0):
        tipo_rcb = 0
    else:
        tipo_rcb = False

    return tipo_rcb


def procesarRB(order, currencyPair):
    """
        Metodo que procesa returnBalances y revisa si existe la moneda a consultar
    :param order: returnBalances (self.rb)
    :param currencyPair: Moneda a consultar, ej: 'BTC'
    :return: order
    """
    if float(order[currencyPair]) < 0:
        order = False
    return order


def promedioBuy(order, polo):
    """
        Metodo para promediar el Monto que queremos comprar
    :param order: marketTradeHist
    :return: float(sum)
    """
    sum = 0.0
    contador = 0
    for ord in order:
        if ord['type'] == 'buy' and contador <= 199:
            sum += float(ord['total'])
            contador +=1
        elif contador >= 200:
            break

    if contador == 200:
        sum = sum / 200
    else:
        mkt = marketTradeHist(polo, 'USDT_BTC', time() - (polo.HOUR * 2))
        promedioBuy(mkt, polo)
    return float("{0:.8f}".format(sum))


def calcularStop(precio_compra, porcentaje_stop):
    """
        Metodo que calcula el valor del Stop
    :param precio_compra: self.precio_compra
    :param porcentaje_stop: self.porcentajeStop
    :return: float(stop)
    """
    stop = precio_compra - (precio_compra * porcentaje_stop)
    return float(stop)


def evaluarStop(valor_vela, stop):
    """
        Metodo que evalua si es necesario mover (más abajo) la venta
        (esto solo sera necesario cuando el precio del Stop este bajando y no alcanzamos a vender todo)
    :param valor_vela: Valor vela Actual (self.valorVela)
    :param stop: Valor calculado de calcularStop (self.stop)
    :return: True o False
    """
    if float(valor_vela) < float(stop):
        return True
    else:
        return False


class ChartDummyRuso(object):
    """ Saves and retrieves chart data to/from mongodb. It saves the chart
    based on candle size, and when called, it will automaticly update chart
    data if needed using the timestamp of the newest candle to determine how
    much data needs to be updated """

    def __init__(self, api, pair, **kwargs):
        """
        pair = market pair
        period = time period of candles (default: 5 Min)
        """
        #definir bien!
        self.porcentajeStop = 0.0024
        self.enProceso = 'hodl'
        self.bandera_iterar_compra = False
        self.bandera_iterar_venta = False
        self.bandera_comprobar_stop = False
        self.orden_venta_stop = 0
        self.stop = 0
        self.contador_bollinger_strat = 0
        self.contador_cantidad_bbtop = 0
        self.contador_cantidad_bbbottom = 0
        self.polo = Poloniex(prop.apikey, prop.apiSecret)
        self.api = api
        self.roo = False
        self.pair = pair
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
            logging.warning('%s collection is empty!',
                           '%s_%s_chart' % (self.pair, str(self.period)))
            # new = self.polo.returnChartData(self.pair,
            #                               period=self.period,
            #                               start=time() - self.polo.YEAR)
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
        logging.info('Updating %s with %s new entrys!',
                    self.pair + '-' + str(self.period), str(updateSize))
        # show progress
        for i in range(updateSize):
            print("\r%s/%s" % (str(i + 1), str(updateSize)), end=" complete ")
            date = new[i]['date']
            del new[i]['date']
            self.db.update_one({'_id': date}, {"$set": new[i]}, upsert=True)
        print('')
        logging.debug('Getting chart data from db')
        # return data from db
        return sorted(list(self.db.find().skip(self.db.find().count() - 288)), key=itemgetter('_id'))

    def dataFrame(self, size=0):
        """
            Metodo que rescata los valores Actuales y calcula los indicadores
        :param size:
        :return: df, (dataFrame con todos los calculos)
        """
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
        # Variables SMA, EMA, RSI
        smaperiod = 50
        ema20 = 20
        ema30 = 30
        # calculate/add sma and bbands
        df = bbands(df, smaperiod)

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
        self.valor_vela_size = df['close'].size - 1
        self.valorVela = float(df['close'].iloc[self.valor_vela_size])
        return df

    def botWhale(self, df):
        """
            -Metodo que recibe senal de venta o compra
            -si la señal es compra, activa StopLimit
            -si la señal es venta, asegura la venta inmediata
        :param df: df
        """
        senal = self.bollinger_strat(df)
        # metodo buy
        if senal > 0 and self.enProceso == 'hodl':
            mkt = marketTradeHist(self.polo, 'USDT_BTC', time() - self.polo.HOUR)
            if mkt:
                monto = promedioBuy(mkt, self.polo)
                self.rcb = returnCompleteBalances(self.polo)
                if monto >= float(self.rcb['USDT']['available']):
                    monto = float(self.rcb['USDT']['available'])

            else:
                logging.error('[botWhale] ERROR!, ocurrio un error al traer marketTradeHist, se vuelve a ejecutar')
                self.botWhale(df)

            order = comprar(self.polo, 'USDT_BTC', self.valorVela, monto)
            if order:
                self.precio_compra = self.valorVela
                self.orden_compra = int(order['orderNumber'])
                self.enProceso = 'compra'
            else:
                logging.error('[botWhale] ERROR!, no se pudo comprar en senal > 0')

        # metodo sell
        elif senal < 0 and self.enProceso == 'compra':
            # mover orden del STOP!
            # order= vender(self.polo, 'USDT_BTC', self.valorVela)
            order = moveOrder(self.polo, self.orden_venta_stop, self.valorVela, False)
            if order:
                self.precio_venta = self.valorVela
                self.orden_venta = int(order['orderNumber'])
                self.enProceso = 'venta'
            else:
                logging.error('[botWhale] ERROR!, no se pudo vender en senal < 0')


        while True:
            # metodo Stop para rescatar
            if self.stop == 0 and self.enProceso == 'compra':
                self.stop = calcularStop(self.precio_compra, self.porcentajeStop)
            elif self.enProceso == 'compra' and not self.bandera_iterar_compra:
                self.roo = True
                self.bandera_iterar_compra = True
                break
            # Verifica si existen ordenes abiertas
            elif self.roo and self.bandera_iterar_compra and self.enProceso == 'compra':
                self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                bandera_compra = False
                # retirar orden de compra si no alcanza a comprar
                if not self.bandera_comprobar_stop:
                    for ord in self.roo:
                        if (ord['type'] == 'buy') and (self.orden_compra == int(ord['orderNumber'])):
                            bandera_compra = True
                            if self.precio_compra > float(df['sma'].iloc[self.valor_vela_size]):
                                cancel = cancelOrder(self.polo, self.orden_compra)
                                logging.debug('[botWhale] Cancele orden, el precio subio demasiado')
                                if cancel:
                                    self.roo.remove(ord)

                    # comprueba si es una orden de compra y ejecuta StopLoss con el monto que disponible
                    self.rcb = returnCompleteBalances(self.polo)
                    self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                    # Comprueba que existan RCB
                    if self.tipo_rcb == 3:
                        order = self.stopLimit()
                        if order == 'stop_realizado':
                            logging.debug('[botWhale] Stop loss realizado, tipo_rcb == 3')
                            break
                        elif order == 'stop_terminado':
                            self.enProceso = 'hodl'
                            self.stop = 0
                            self.bandera_iterar_compra = False
                            self.bandera_comprobar_stop = False
                            self.orden_venta_stop = 0
                            self.precio_compra = 0
                            self.orden_compra = 0
                            self.roo = False
                            self.tipo_rcb = False
                            logging.debug('[botWhale] Stop loss terminado, tipo_rcb == 3')
                            break
                        elif not order:
                            logging.error('[botWhale] ERROR!, stopLimit con ordenes abiertas y monto disponible en problemas!, se repite el proceso')
                            continue

                    elif self.tipo_rcb == 2 and not bandera_compra:
                        self.bandera_comprobar_stop = True
                        order = self.stopLimit()
                        if order == 'stop_terminado':
                            self.enProceso = 'hodl'
                            self.stop = 0
                            self.bandera_iterar_compra = False
                            self.bandera_comprobar_stop = False
                            self.orden_venta_stop = 0
                            self.precio_compra = 0
                            self.orden_compra = 0
                            self.roo = False
                            self.tipo_rcb = False
                            logging.debug('[botWhale] Stop loss terminado, tipo_rcb == 2')
                            break
                        elif order == 'stop_normal':
                            logging.debug('[botWhale] Stop sigue normal y en revision')
                            break
                        elif not order:
                            logging.error('[botWhale] ERROR!, stopLimit con solo ordenes abiertas en problemas!, se repite el proceso')
                            continue
                        break

                    elif self.tipo_rcb == 2 and bandera_compra:
                        #no realiza nada y espera el siguiente ciclo
                        break

                    elif self.tipo_rcb == 1:
                        order = self.stopLimit()
                        if order == 'stop_realizado':
                            self.bandera_comprobar_stop = True
                            logging.debug('[botWhale] Stop loss colocado, tipo_rcb == 1')
                            break
                        elif order == 'stop_terminado':
                            self.enProceso = 'hodl'
                            self.stop = 0
                            self.bandera_iterar_compra = False
                            self.bandera_comprobar_stop = False
                            self.orden_venta_stop = 0
                            self.precio_compra = 0
                            self.orden_compra = 0
                            self.roo = False
                            self.tipo_rcb = False
                            logging.debug('[botWhale] Stop loss terminado, tipo_rcb == 1')
                            break
                        elif not order:
                            logging.error(
                                '[botWhale] ERROR!, stopLimit con monto disponible en problemas!, se repite el proceso')
                            continue

                    elif self.tipo_rcb == 0:
                        self.enProceso = 'hodl'
                        self.stop = 0
                        self.bandera_iterar_compra = False
                        self.bandera_comprobar_stop = False
                        self.orden_venta_stop = 0
                        self.precio_compra = 0
                        self.orden_compra = 0
                        self.roo = False
                        self.tipo_rcb = False
                        print('Stop loss terminado, tipo_rcb == 0')
                        break

                    else:
                        print('[botWhale] No existe tipo_rcb 1, 2 o 3, se repite secuencia')
                        continue

                # Si solo existen ordenes abiertas, ingresa a este Stop, el cual estara comprobando el valor_vela con self.stop
                elif self.roo and self.bandera_comprobar_stop:
                    order = self.stopLimit()
                    if order == 'stop_terminado':
                        self.enProceso = 'hodl'
                        self.stop = 0
                        self.bandera_iterar_compra = False
                        self.bandera_comprobar_stop = False
                        self.orden_venta_stop = 0
                        self.precio_compra = 0
                        self.orden_compra = 0
                        self.roo = False
                        self.tipo_rcb = False
                        print('Stop loss terminado, bandera_comprobar_stop = True')
                        break
                    elif order == 'stop_normal':
                        print('Stop sigue normal y en revision, bandera_comprobar_stop = True')
                        break
                    elif not order:
                        print(
                            '[botWhale] ERROR!, stopLimit con solo ordenes abiertas en problemas!, se repite el proceso')
                        continue

            # metodo Stop para vender
            elif self.enProceso == 'venta' and not self.bandera_iterar_venta:
                self.bandera_iterar_venta = True
                self.roo = True
                break

            elif self.enProceso == 'venta' and self.bandera_iterar_venta and self.roo:
                self.comprobarVenta()
                break
            else:
                print('[botWhale] Mantener en HODL')
                break

    def stopLimit(self):
        """
            Metodo que realiza StopLoss con sus distintas posibilidades, los parametros son entregados en Self
            :param tipo_rcb: Datos traidos del metodo procesarRCB
            :param orden_venta_stop: Orden de venta al dejar el StopLoss activo
            :param roo: datos de returnOpenOrders
            :param bandera_comprobar_stop: Bandera que es asignada en el While Compra, del metodo botWhale

        :return: String
        """
        #Evalua si se requiere actualizar el Stoploss
        evaluar_stop = evaluarStop(self.valorVela, self.stop)
        if (self.tipo_rcb == 1 or self.tipo_rcb == 3) and self.orden_venta_stop == 0:
            order = vender(self.polo, 'USDT_BTC', self.valorVela, float(self.rcb['BTC']['available']))
            if float(order['resultingTrades']['amount']) == float(self.rcb['BTC']['available']):
                return 'stop_terminado'
            elif order:
                self.orden_venta_stop = int(order['orderNumber'])
                return 'stop_realizado'
            else:
                self.stopLimit()

        roo_stop = False
        for ord in self.roo:
            if (ord['type'] == 'sell') and (self.orden_venta_stop == int(ord['orderNumber'])):
                roo_stop = ord

        if roo_stop and self.tipo_rcb == 3:
            monto_total = 0
            for ord in roo_stop:
                monto_total += float(ord['amount'])

            monto_total += float(self.rcb['BTC']['available'])
            order = moveOrder(self.polo, self.orden_venta_stop, self.valorVela, monto_total)
            #if float(order['resultingTrades']['amount']) == monto_total):     REVISAR!, VERIFICAR SI MONTO TOTAL AL MOVER ES IGUAL AL AMOUNT DEL RESULTINGTRADES

            if order:
                self.orden_venta_stop = int(order['orderNumber'])
                return 'stop_realizado'
            else:
                self.stopLimit()

        elif evaluar_stop and roo_stop and self.tipo_rcb == 2:
            order = moveOrder(self.polo, self.orden_venta_stop, self.valorVela, False)
            if order:
                for ord in roo_stop:
                    if float(order['resultingTrades']['amount']) == float(ord['amount']):
                        return 'stop_terminado'
                self.orden_venta_stop = int(order['orderNumber'])
                logging.debug('[stopLimit], se corrige stopLimit, se repite para vender todo!')
                self.dataFrame()
                self.stopLimit()
            else:
                self.stopLimit()

        elif self.tipo_rcb == 2 and not roo_stop:
            print('[stopLimit] Se vendieron todos los stopLimit')
            return 'stop_terminado'

        elif roo_stop and not evaluar_stop and self.bandera_comprobar_stop:
            return 'stop_normal'

        else:
            print('[stopLimit] ERROR!, no cayo en ningun if...')
            return False

    def bollinger_strat(self, df, targetcol='close'):
        """
            Metodo que calcula cuando dar senal de venta o compra
            los parametros son entregados en Self, excepto df
                - senal < 0 = senal de VENTA
                - senal > 0 = senal de COMPRA
        :param df: df
        :param valor_vela_size: index de la vela actual
        :param contador_bollinger_strat: Contador para comprobar que una vela supero al bbtop de forma excesiva
        :return: senal
        """
        percent = 0.00025
        percent_contador = 0.00015
        valor_venta = float(df['bbtop'].iloc[self.valor_vela_size]) + (float(df['bbtop'].iloc[self.valor_vela_size]) * percent)
        valor_percent_contador = float(df['bbtop'].iloc[self.valor_vela_size]) + (float(df['bbtop'].iloc[self.valor_vela_size]) * percent_contador)

        #############################
        ####      REVISAR       #####
        ##############################

        # Comprueba si la vela supero al 'bbtop'
        if (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size] > valor_percent_contador):
            self.contador_bollinger_strat += 1
        #Si la vela bajo del bbtop (despues de haberlo superado), reinicia el contador y Vende
        if self.contador_bollinger_strat > 0 and (
                df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]):
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbtop = 0
            self.contador_cantidad_bbbottom = 0
            senal = -1
            logging.debug('[bollinger_strat] SENAL Venta= '+str(senal))
            return senal
        if df[targetcol].iloc[self.valor_vela_size] > df['bbtop'].iloc[self.valor_vela_size] or(
                df[targetcol].iloc[self.valor_vela_size] > df['high'].iloc[self.valor_vela_size]):
            self.contador_cantidad_bbtop += 1
        if df[targetcol].iloc[self.valor_vela_size] < df['bbbottom'].iloc[self.valor_vela_size] or (
                df[targetcol].iloc[self.valor_vela_size] < df['low'].iloc[self.valor_vela_size]):
            self.contador_cantidad_bbbottom += 1

        if (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] <= df['bbtop'].iloc[self.valor_vela_size - 1]) and (
                df[targetcol].iloc[self.valor_vela_size] < valor_venta) and(
                self.contador_bollinger_strat > 1 or self.contador_bollinger_strat == 0) and (
                self.contador_cantidad_bbtop >= 1):
            senal = -2
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbtop = 0
            self.contador_cantidad_bbbottom = 0
            logging.debug('[bollinger_strat] SENAL Venta= ' + str(senal))

        elif (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['bbtop'].iloc[self.valor_vela_size - 1] or
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['high'].iloc[self.valor_vela_size - 1]) and (
                df[targetcol].iloc[self.valor_vela_size] < valor_venta) and (
                self.contador_bollinger_strat > 1 or self.contador_bollinger_strat == 0) and (
                self.contador_cantidad_bbtop >= 1):
            #lo mas probable es que este caso no ocurra, pero se deja por precaucion
            senal = -3
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbtop = 0
            self.contador_cantidad_bbbottom = 0
            logging.debug('[bollinger_strat] SENAL Venta= ' + str(senal))

        elif (df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['bbtop'].iloc[self.valor_vela_size - 1] or
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['high'].iloc[self.valor_vela_size - 1]) and (
                self.contador_cantidad_bbtop >= 1):
            senal = -4
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbtop = 0
            self.contador_cantidad_bbbottom = 0
            logging.debug('[bollinger_strat] SENAL Venta= ' + str(senal))

        elif self.contador_cantidad_bbtop > 0 and (
                df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]):
            self.contador_cantidad_bbtop = 0
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbbottom = 0
            senal = -5
            logging.debug('[bollinger_strat] SENAL Venta= ' + str(senal))

        elif (df[targetcol].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] <= df['bbbottom'].iloc[self.valor_vela_size - 1] or
                self.contador_cantidad_bbbottom > 0):
            self.contador_cantidad_bbtop = 0
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbbottom = 0
            senal = 1
            logging.debug('[bollinger_strat] SENAL Compra= ' + str(senal))

        elif (df[targetcol].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size]) and (
                df['low'].iloc[self.valor_vela_size - 1] <= df['bbbottom'].iloc[self.valor_vela_size - 1]) and (
                self.contador_cantidad_bbbottom > 0):
            self.contador_cantidad_bbtop = 0
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbbottom = 0
            senal = 2
            logging.debug('[bollinger_strat] SENAL Compra= ' + str(senal))

        else:
            senal = 0
            logging.debug('[bollinger_strat] SENAL = ' + str(senal))

        return senal

    def comprobarVenta(self):
        """
            Metodo que comprueba si la venta aun existe, si es asi modifica el precio para asegurar la venta
            los parametros son entregados en Self
        :param precio_venta: Precio al cual fue vendida la divisa
        :param valorVela: Valor actual de la vela
        :param orden_venta: Numero de orden de Venta
        :param polo: api Poloniex (self.polo)
        :return:
        """
        self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
        if self.roo:
            for ord in self.roo:
                if (ord['type'] == 'sell') and (self.orden_venta == int(ord['orderNumber'])) and (
                        self.precio_venta > self.valorVela):
                    move = moveOrder(self.polo, self.orden_venta, self.valorVela, False)
                    if float(move['resultingTrades']['amount']) == float(ord['amount']):
                        self.bandera_iterar_venta = False
                        self.enProceso = 'hodl'
                        self.stop = 0
                        self.orden_venta_stop = 0
                        self.orden_venta = 0
                        self.precio_venta = 0
                        self.roo = False
                        self.bandera_iterar_compra = False
                        self.tipo_rcb = False
                        self.precio_compra = 0
                        self.orden_compra = 0
                        self.bandera_comprobar_stop = False
                        logging.debug('[comprobarVenta] Se vende todo en BTC!')
                    elif move:
                        self.orden_venta = int(move['orderNumber'])
                        self.precio_venta = self.valorVela
                        self.dataFrame()
                        self.comprobarVenta()
                    else:
                        logging.error(
                            '[comprobarVenta] ERROR!, No se pudo mover la orden para actualizar venta!, se repite el proceso')
                        self.comprobarVenta()
                else:
                    logging.debug('[comprobarVenta] Mantener en Venta')

        else:
            self.bandera_iterar_venta = False
            self.enProceso = 'hodl'
            self.stop = 0
            self.orden_venta_stop = 0
            self.orden_venta = 0
            self.precio_venta = 0
            self.roo = False
            self.bandera_iterar_compra = False
            self.tipo_rcb = False
            self.precio_compra = 0
            self.orden_compra = 0
            self.bandera_comprobar_stop = False
            logging.debug('[comprobarVenta] Se vende todo en BTC!')

    def ejecuta(self):
        """
            Demonio que ejecuta infinitamente el Bot
        :return:
        """
        print('entre al ejecuta')
        try:
            while True:
                df=self.dataFrame()
                self.botWhale(df)
                print('YA DI LA VUELTA!')
        except Exception as err:
            logging.error('[ejecuta] Error!, vuelve a ejecutar!, '+err)
            self.ejecuta()


if __name__ == '__main__':
    from poloniex import Poloniex

    logging.basicConfig(filename='ChartDummyRuso.log', level=logging.DEBUG)
    logging.getLogger(__name__)
    api = Poloniex(jsonNums=float)
    ChartDummyRuso(api, 'USDT_BTC').ejecuta()

