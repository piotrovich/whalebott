from __future__ import print_function
from time import time, sleep
import logging
from operator import itemgetter
from pymongo import MongoClient
import pandas as pd
import numpy as np
import prop
import datetime


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
        valor_monto = calcularFloat(monto)
        comprar = polo.buy(currencyPair, valor_vela, valor_monto)
    except Exception as err:
        logger.error('[comprar] Error!: '+str(err))
        comprar = False
    return comprar


def vender(polo, currencyPair, valor_vela, monto):
    """
        metodo vender
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :param valor_vela: Valor actual de la vela (self.valorVela)
    :param monto: monto calculado que se Vendera (float)
    :return: vender
    """
    try:
        valor_monto = calcularFloat(monto)
        vender = polo.sell(currencyPair, valor_vela, valor_monto)
    except Exception as err:
        logger.error('[vender] Error!: ' + str(err))
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
        logger.debug('[moveOrder] Ingrese a moveOrder, order_number: ' + str(order_number) + ', valor_vela: ' +
                     str(valor_vela) + ', amount: ' + str(amount))
        if not amount:
            logger.debug('[moveOrder] if not amount:')
            order = polo.moveOrder(order_number, valor_vela)
            logger.debug('[moveOrder] order: ' + str(order))
        else:
            valor_monto = calcularFloat(amount)
            logger.debug('[moveOrder] if not amount:')
            order = polo.moveOrder(order_number, valor_vela, valor_monto)
            logger.debug('[moveOrder] order: ' + str(order))
        if order['success'] != 1:
            order = False
    except Exception as err:
        logger.error('[moveOrder] Error!: ' + str(err))
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
    except Exception as err:
        logger.error('[returnOpenOrders] Error!: ' + str(err))
        order = False
    return order


def returnCompleteBalances(polo):
    """
        Metodo que retorna los balances (disponible, en orden y calculado en BTC)
    :param polo: api Poloniex (self.polo)
    :return: order
    """
    try:
        order = polo.returnCompleteBalances()
    except Exception as err:
        logger.error('[returnCompleteBalances] Error!: ' + str(err))
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
    except Exception as err:
        logger.error('[returnBalances] Error!: ' + str(err))
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
    except Exception as err:
        logger.error('[cancelOrder] Error!: ' + str(err))
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
    except Exception as err:
        logger.error('[marketTradeHist] Error!: ' + str(err))
        order = False
    return order


def returnTradeHistory(polo, currencyPair, start):
    """
        Retorna nuestro mercado  historico en un tiempo designado
    :param polo: api Poloniex (self.polo)
    :param currencyPair: mercado a consultar, ej: 'USDT_BTC'
    :param start: Tiempo desde cuando se requiere el historico
    :return:
    """
    try:
        order = polo.returnTradeHistory(currencyPair, start)
    except Exception as err:
        logger.error('[returnTradeHistory] Error!: ' + str(err))
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
        logger.error('[procesarRCB] tipo_rcb = False')
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
        mkt = marketTradeHist(polo, 'USDT_BTC', time() - (polo.HOUR * 4))
        promedioBuy(mkt, polo)

    valor_sum = calcularFloat(sum)
    return valor_sum


def calcularStop(precio_compra, porcentaje_stop):
    """
        Metodo que calcula el valor del Stop
    :param precio_compra: self.precio_compra
    :param porcentaje_stop: self.porcentajeStop
    :return: float(stop)
    """
    stop = precio_compra - (precio_compra * porcentaje_stop)
    valor_stop = calcularFloat(stop)
    return valor_stop


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


class IniciaChart(object):
    def __init__(self):
        ChartDummy('USDT_BTC').ejecuta()


class ChartDummy(IniciaChart):
    """ Saves and retrieves chart data to/from mongodb. It saves the chart
    based on candle size, and when called, it will automaticly update chart
    data if needed using the timestamp of the newest candle to determine how
    much data needs to be updated """

    def __init__(self, pair, **kwargs):
        """
        pair = market pair
        period = time period of candles (default: 5 Min)
        """
        from poloniex import Poloniex
        self.max_loop = 80
        self.count_loop = 0
        # definir bien!
        #self.porcentajeStop = 0.0024
        self.porcentajeStop = 0.02
        self.orden_venta_stop, self.stop, self.contador_bollinger_strat = 0, 0, 0
        self.contador_cantidad_bbbottom, self.precio_venta_stop = 0, 0
        self.date3hour = datetime.datetime.today() + datetime.timedelta(hours=3)
        self.date18hour = datetime.datetime.today() + datetime.timedelta(hours=18)
        self.polo = Poloniex(prop.apikey, prop.apiSecret)
        self.api = Poloniex(jsonNums=float)
        self.roo = False
        self.pair = pair
        self.period = kwargs.get('period', self.api.MINUTE * 5)
        self.db = MongoClient()['poloniex']['%s_%s_chart' %
                                            (self.pair, str(self.period))]
        self.comprobar_init()
        #self.enProceso = 'hodl'

    def no_loop(self):
        """
            Metodo que comprueba que el Bot no quede en un loop infinito
        :return:
        """
        self.count_loop += 1
        if self.count_loop > self.max_loop:
            logger.debug('[no_loop] if self.count_loop > self.max_loop:')
            super().__init__()

    def reboot(self):
        """
            Metodo que Reinicia Bot cada 18 horas
        :return:
        """
        if self.date18hour < datetime.datetime.today():
            logger.debug('[reboot] REBOOT!')
            super().__init__()

    def comprobar_init(self):
        """
            Metodo que comprueba estado de self.enProceso al iniciar el BOT
        :return: self.enProceso
        """
        self.enProceso = 'hodl'
        while True:
            try:
                logger.debug('[comprobar_init] ingrese a comprobar_init')
                sleep(1)
                self.rcb = returnCompleteBalances(self.polo)
                logger.debug('[comprobar_init] correccion de compras')
                if float(self.rcb['USDT']['onOrders']):
                    logger.debug('[comprobar_init] Existen USDT en orden')
                    self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                    if self.roo:
                        logger.debug('[comprobar_init] if self.roo:')
                        for roousdt in self.roo:
                            if roousdt['type'] == 'buy':
                                self.precio_compra = float(roousdt['rate'])
                                self.orden_compra = int(roousdt['orderNumber'])
                                break
                        df = self.dataFrame()
                        senal = self.bollinger_strat(df)
                        if senal > 0:
                            logger.debug('[comprobar_init] if senal > 0:')
                            self.comprobarCompra()
                        else:
                            logger.debug('[comprobar_init] No es momento de comprar, se cancela la orden')
                            cancel = cancelOrder(self.polo, self.orden_compra)
                            if cancel:
                                self.enProceso = 'hodl'
                            else:
                                logger.error('[comprobar_init] ERROR! cancel con problemas, se vuelve a '
                                             'ejecutar comprobar_init')
                                self.no_loop()
                                sleep(1)
                                continue
                    else:
                        logger.debug('[comprobar_init] Se ejecutaron las ordenes, se vuelve a ejecutar para estar '
                                     'seguros del proceso ')
                        sleep(1)
                        continue

                sleep(1)
                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                logger.debug('[comprobar_init] tipo_rcb: BTC, correccion de ventas')
                if self.tipo_rcb == 1 or self.tipo_rcb == 2 or self.tipo_rcb == 3:
                    logger.debug('[comprobar_init] self.tipo_rcb == 1 or self.tipo_rcb == 2 or self.tipo_rcb == 3')
                    order = returnTradeHistory(self.polo, 'USDT_BTC', time() - (self.api.DAY * 5))
                    df = self.dataFrame()
                    if self.tipo_rcb == 1:
                        logger.debug('[comprobar_init] order and self.tipo_rcb == 1')
                        if order:
                            for ord in order:
                                if ord['type'] == 'buy':
                                    if float(ord['rate']) < df['bbbottom'].iloc[self.valor_vela_size]:
                                        self.precio_compra = float(df['bbbottom'].iloc[self.valor_vela_size])
                                    else:
                                        self.precio_compra = float(ord['rate'])
                                    self.orden_compra = int(ord['orderNumber'])
                                    self.enProceso = 'compra'
                                break
                        else:
                            self.precio_compra = calcularFloat(df['bbbottom'].iloc[self.valor_vela_size])
                            self.enProceso = 'compra'

                    elif self.tipo_rcb == 2 or self.tipo_rcb == 3:
                        logger.debug('[comprobar_init] order and (self.tipo_rcb == 2 or self.tipo_rcb == 3)')
                        self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                        if self.roo:
                            logger.debug('[comprobar_init] if self.roo:')
                            for roobtc in self.roo:
                                if roobtc['type'] == 'sell':
                                    self.precio_venta = float(roobtc['rate'])
                                    self.orden_venta = int(roobtc['orderNumber'])
                            df = self.dataFrame()
                            if order:
                                for ord in order:
                                    if ord['type'] == 'buy':
                                        if float(ord['rate']) < df['bbbottom'].iloc[self.valor_vela_size]:
                                            self.precio_compra = calcularFloat(df['bbbottom'].iloc[self.valor_vela_size])
                                        else:
                                            self.precio_compra = float(ord['rate'])
                                        self.orden_compra = int(ord['orderNumber'])
                                    break
                            else:
                                self.precio_compra = calcularFloat(df['bbbottom'].iloc[self.valor_vela_size])
                                self.enProceso = 'compra'

                            self.stop = calcularStop(calcularFloat(df['bbbottom'].iloc[self.valor_vela_size]), self.porcentajeStop)
                            evaluar_stop = evaluarStop(self.valorVela, self.stop)
                            if evaluar_stop:
                                logger.debug('[comprobar_init] if evaluar_stop:')
                                self.orden_venta_stop = self.orden_venta
                                stop_limit = self.stopLimit()
                                if stop_limit:
                                    logger.debug('[comprobar_init] if stop_limit:, [precio_venta_stop: ' + str(
                                        self.precio_venta_stop)+']')
                                    self.enProceso = 'hodl'
                                    self.stop, self.orden_venta_stop, self.orden_venta, self.precio_venta = 0, 0, 0, 0
                                    self.roo, self.tipo_rcb, self.rcb = False, False, False
                                    self.precio_compra, self.orden_compra, self.precio_venta_stop = 0, 0, 0
                                else:
                                    logger.error('[comprobar_init] ELSE => if stop_limit:, ocurrio un error, se repite')
                                    self.no_loop()
                                    sleep(0.5)
                                    continue
                            else:
                                logger.debug('[comprobar_init] ELSE => stop_limit:')
                                senal = self.bollinger_strat(df)
                                if senal < 0:
                                    logger.debug('[comprobar_init] if senal < 0:')
                                    self.comprobarVenta()
                                    if self.tipo_rcb == 3:
                                        logger.debug('[comprobar_init] if self.tipo_rcb == 3:')
                                        self.vender_whale()
                                else:
                                    logger.debug('[comprobar_init] La orden no se encuentra en stop ni en senal'
                                                 ' < 0, se cancela orden activa y self.enProceso = compra')
                                    cancel = cancelOrder(self.polo, self.orden_venta)
                                    if cancel:
                                        self.enProceso = 'compra'
                                    else:
                                        logger.error('[comprobar_init] ERROR! cancel con problemas, se vuelve a '
                                                     'ejecutar comprobar_init')
                                        self.no_loop()
                                        continue
                        else:
                            logger.debug('[comprobar_init] ELSE => self.roo:')
                            continue
                else:
                    pass
                sleep(1)
                logger.debug('[comprobar_init] Termine a comprobar_init')
                break

            except Exception as err:
                logger.error('[comprobar_init] Error!, ' + str(err))
                self.no_loop()
                continue

        self.count_loop = 0

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
            # new = self.polo.returnChartData(self.pair,
            #                               period=self.period,
            #                               start=time() - self.polo.YEAR)
            new = self.api.returnChartData(self.pair, period=self.period, start=time() - self.api.DAY)
        # we have data in db already
        else:
            new = self.api.returnChartData(self.pair, period=self.period, start=int(last['_id']))
        # add new candles
        updateSize = len(new)
        # show progress
        for i in range(updateSize):
            print("\r%s/%s" % (str(i + 1), str(updateSize)), end=" complete ")
            date = new[i]['date']
            del new[i]['date']
            self.db.update_one({'_id': date}, {"$set": new[i]}, upsert=True)
        print('')
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

    def whaleBot(self, df):
        """
            -Metodo que recibe senal de venta o compra
            -si la señal es compra, activa StopLimit
            -si la señal es venta, asegura la venta inmediata
        :param df: df
        """
        while True:
            try:
                senal = self.bollinger_strat(df)
                #####################
                #       DUMMY       #
                #####################
                #self.comprobarCompra()
                # metodo buy
                if senal > 0 and self.enProceso == 'hodl':
                    logger.debug('[whaleBot] Ingrese: senal > 0 and self.enProceso == hodl')
                    self.comprar_whale()
                    ##########################
                    #   Se agrega para pruebas
                    ##########################
                    sleep(0.7)
                    self.rcb = returnCompleteBalances(self.polo)
                    logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['USDT']['available']))
                    logger.debug('[whaleBot] balance completo BTC: ' + str(self.rcb['BTC']['available']))
                    self.rcb = False

                # metodo sell
                elif senal < 0 and self.enProceso == 'compra':
                    logger.debug('[whaleBot] Ingrese: senal < 0 and self.enProceso == compra')
                    self.rcb = returnCompleteBalances(self.polo)
                    self.vender_whale()
                    ##########################
                    #   Se agrega para pruebas
                    ##########################
                    sleep(0.7)
                    self.rcb = returnCompleteBalances(self.polo)
                    logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['USDT']['available']))
                    logger.debug('[whaleBot] balance completo BTC: ' + str(self.rcb['BTC']['available']))
                    self.rcb = False

                if self.enProceso == 'compra':
                    self.stop = calcularStop(float(df['bbbottom'].iloc[self.valor_vela_size]), self.porcentajeStop)
                    evaluar_stop = evaluarStop(self.valorVela, self.stop)
                    #Comprueba si es necesario realizar el StopLimit
                    if evaluar_stop:
                        logger.debug('[whaleBot] evaluar Stop: ' + str(evaluar_stop) + '[valorVela: ' +str(
                                      self.valorVela) + ']')
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        # Comprueba que existan RCB
                        if self.tipo_rcb == 3 or self.tipo_rcb == 2 or self.tipo_rcb == 1:
                            logger.debug('[whaleBot] self.tipo_rcb == 3 and self.tipo_rcb == 2 and self.tipo_rcb == 1')
                            order = self.stopLimit()
                            if order == 'stop_terminado':
                                logger.debug('[whaleBot] Stop loss terminado, tipo_rcb == ' + str(self.tipo_rcb))
                                self.enProceso = 'hodl'
                                self.stop, self.orden_venta_stop, self.precio_compra, self.orden_compra = 0, 0, 0, 0
                                self.roo, self.tipo_rcb, self.precio_venta_stop, self.rcb = False, False, 0, False
                                ##########################
                                #   Se agrega para pruebas
                                ##########################
                                sleep(0.7)
                                self.rcb = returnCompleteBalances(self.polo)
                                logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['USDT']['available']))
                                logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['BTC']['available']))
                                self.rcb = False
                                break
                            elif not order:
                                logger.error('[whaleBot] ERROR!, no se pudo generar StopLimit!, se repite el proceso')
                                self.no_loop()
                                df = self.dataFrame()
                                continue
                        elif self.tipo_rcb == 0:
                            logger.debug('[whaleBot] self.tipo_rcb == 0 ')
                            self.enProceso = 'hodl'
                            self.stop, self.orden_venta_stop, self.precio_compra, self.orden_compra = 0, 0, 0, 0
                            self.roo, self.tipo_rcb, self.precio_venta_stop, self.rcb = False, False, 0, False
                            logger.debug('[whaleBot] Stop loss terminado, tipo_rcb == 0')
                            ##########################
                            #   Se agrega para pruebas
                            ##########################
                            sleep(0.7)
                            self.rcb = returnCompleteBalances(self.polo)
                            logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['USDT']['available']))
                            logger.debug('[whaleBot] balance completo USDT: ' + str(self.rcb['BTC']['available']))
                            self.rcb = False
                            break
                        else:
                            logger.error('[whaleBot] No existe tipo_rcb 1, 2 o 3, se repite secuencia')
                            self.no_loop()
                            df = self.dataFrame()
                            continue
                    else:
                        #valor vela no a bajado del stop, continua flujo normal
                        break
                else:
                    break
            except Exception as err:
                logger.error('[whaleBot] ERROR! whaleBot se a caido, ' + str(err))
                self.no_loop()
                sleep(0.5)
                df = self.dataFrame()
                continue

        self.count_loop = 0

    def comprobar_en_proceso(self):
        """
            Metodo que comprueba estado self.enProceso para evitar loops en metodos comprar_whale, vender_whale,
            stopLimit, comprobarVenta y comprobarCompra
        :return: self.enProceso
        """
        while True:
            try:
                logger.debug('[comprobar_en_proceso] ingrese a comprobar_en_proceso')
                self.rcb = returnCompleteBalances(self.polo)
                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                if self.tipo_rcb == 0:
                    logger.debug('[comprobar_en_proceso] self.enProceso = hodl')
                    self.enProceso = 'hodl'
                    break
                else:
                    logger.debug('[comprobar_en_proceso] self.enProceso = compra')
                    self.enProceso = 'compra'
                    break
            except Exception as err:
                logger.error('[comprobar_en_proceso] ERROR! comprobar_en_proceso se a caido, ' + str(err))
                continue

    def comprar_whale(self):
        """
            Metodo que compra Criptomonedas, si no puede compra todo va al metodo self.comprobarCompra
        :return:
        """
        while True:
            try:
                logger.debug('[comprar_whale] ingrese a comprar_whale')
                mkt = marketTradeHist(self.polo, 'USDT_BTC', time() - (self.polo.HOUR * 2))
                if mkt:
                    ########################################################
                    #   CORROBORAR SI ES MEJOR MEDIA, MEDIANA O MODA
                    ########################################################
                    monto_usdt = promedioBuy(mkt, self.polo)
                    logger.debug('[comprar_whale] promedio monto en USDT: ' + str(monto_usdt))
                    self.rcb = returnCompleteBalances(self.polo)
                    logger.debug('[comprar_whale] Monto disponible USDT: ' + str(self.rcb['USDT']['available']))
                    if monto_usdt >= float(self.rcb['USDT']['available']):
                        monto_usdt = float(self.rcb['USDT']['available'])
                else:
                    logger.error('[comprar_whale] ERROR!, ocurrio un error al traer '
                                 'marketTradeHist, se vuelve a ejecutar')
                    self.no_loop()
                    sleep(0.5)
                    continue
                nuevo_precio_compra = calcularFloat(self.valorVela + (self.valorVela * 0.0001))
                valor_monto = calcular_monto(monto_usdt, nuevo_precio_compra)
                logger.debug('[comprar_whale] Calcule monto en USDT: ' + str(monto_usdt))
                logger.debug('[comprar_whale] comprar USDT_BTC: [precio_compra: ' + str(nuevo_precio_compra) + '], '
                             '[valor_monto: ' + str(valor_monto) + ']')
                order = comprar(self.polo, 'USDT_BTC', nuevo_precio_compra, valor_monto)
                logger.debug('[comprar_whale] Compre!: ' + str(order))
                if order:
                    self.precio_compra = nuevo_precio_compra
                    self.orden_compra = int(order['orderNumber'])
                    if order['resultingTrades']:
                        amount_for = 0
                        for ord in order['resultingTrades']:
                            amount_for += float(ord['amount'])
                        if amount_for == valor_monto:
                            # Se completa la compra y prosigue con el While
                            self.enProceso = 'compra'
                            logger.debug('[comprar_whale] Orden comprada, monto: ' +
                                         str(amount_for) + ' , precio de compra: ' + str(self.precio_compra))
                            sleep(1)
                            break
                        else:
                            logger.debug('[comprar_whale] ELSE => amount_for == valor_monto:')
                            self.comprobarCompra()
                            logger.debug('[comprar_whale] Orden comprada')
                            sleep(1)
                            break
                    else:
                        logger.debug('[comprar_whale] ELSE => order[resultingTrades]:')
                        self.comprobarCompra()
                        logger.debug('[comprar_whale] Orden comprada')
                        sleep(1)
                        break
                else:
                    logger.error('[comprar_whale] ERROR!, no se pudo comprar en senal > 0')
                    self.no_loop()
                    self.dataFrame()
                    continue

            except Exception as err:
                logger.error('[comprar_whale] ERROR! comprar_whale se a caido, ' + str(err))
                self.no_loop()
                sleep(0.5)
                self.comprobar_en_proceso()
                if self.enProceso == 'hodl':
                    self.dataFrame()
                    continue
                else:
                    sleep(1)
                    break

        self.count_loop = 0

    def vender_whale(self):
        """
            Metodo que vende Criptomonedas, si no puede vender todo va al metodo self.comprobarVenta
            :param valorVela = Valor actual de la vela
            :param rcb = Return Complete Balances, se utiliza para calcular el monto total a vender
        :return:
        """
        while True:
            try:
                logger.debug('[vender_whale] ingrese a vender_whale')
                monto = float(self.rcb['BTC']['available'])
                nuevo_precio_venta = calcularFloat(self.valorVela - (self.valorVela * 0.0001))
                logger.debug('[vender_whale] Vender USDT_BTC: [nuevo_precio_venta: ' + str(nuevo_precio_venta) +
                             '], [valor_monto: ' + str(monto) + ']')
                order = vender(self.polo, 'USDT_BTC', nuevo_precio_venta, monto)
                logger.debug('[vender_whale] Vendi!: ' + str(order))
                if order:
                    self.precio_venta = nuevo_precio_venta
                    self.orden_venta = int(order['orderNumber'])
                    if order['resultingTrades']:
                        amount_for = 0
                        for ord in order['resultingTrades']:
                            amount_for += float(ord['amount'])
                        if amount_for == monto:
                            # Se completa la venta, termina el proceso
                            logger.debug('[vender_whale] Se vende todo en BTC!, [precio_venta: ' + str(
                                self.precio_venta) + ']')
                            self.enProceso = 'hodl'
                            self.stop, self.orden_venta_stop, self.orden_venta, self.precio_venta = 0, 0, 0, 0
                            self.roo, self.tipo_rcb, self.rcb = False, False, False
                            self.precio_compra, self.orden_compra, self.precio_venta_stop = 0, 0, 0
                            break
                        else:
                            logger.debug('[vender_whale] no se vendio todo, ingresa a comprobarVenta')
                            self.comprobarVenta()
                            break
                    else:
                        logger.debug('[vender_whale] no se vendio todo, ingresa a comprobarVenta')
                        self.comprobarVenta()
                        break
                else:
                    logger.error('[vender_whale] ERROR!, no se pudo vender en senal < 0')
                    self.no_loop()
                    sleep(0.5)
                    self.rcb = returnCompleteBalances(self.polo)
                    self.dataFrame()
                    continue
            except Exception as err:
                logger.error('[vender_whale] ERROR! vender_whale se a caido, ' + str(err))
                self.no_loop()
                sleep(0.5)
                self.comprobar_en_proceso()
                if self.tipo_rcb == 3:
                    logger.debug('[vender_whale] if self.tipo_rcb == 2 or self.tipo_rcb == 3:')
                    self.comprobarVenta()
                    self.dataFrame()
                    continue
                elif self.tipo_rcb == 2:
                    self.comprobarVenta()
                    break
                if self.enProceso == 'compra':
                    self.dataFrame()
                    continue
                else:
                    sleep(1)
                    break

        self.count_loop = 0

    def stopLimit(self):
        """
            Metodo que realiza StopLoss con sus distintas posibilidades, los parametros son entregados en Self
            :param tipo_rcb: Datos traidos del metodo procesarRCB
            :param orden_venta_stop: Orden de venta al dejar el StopLoss activo
            :param roo: datos de returnOpenOrders
        :return: String
        """
        while True:
            try:
                logger.debug('[stopLimit] Inicio Stop, valor tipo_rcb: ' + str(self.tipo_rcb))
                roo_stop = False
                nuevo_precio_venta_stop = calcularFloat(self.valorVela - (self.valorVela * 0.0001))
                if (self.tipo_rcb == 1 or self.tipo_rcb == 3) and self.orden_venta_stop == 0:
                    logger.debug('[stopLimit] self.tipo_rcb == 1 or self.tipo_rcb == 3) and self.orden_venta_stop == 0:')
                    logger.debug('[stopLimit] Vender USDT_BTC: [nuevo_precio_venta_stop: ' + str(nuevo_precio_venta_stop)
                                 +'], [monto: ' + str(self.rcb['BTC']['available']) + ']')
                    order = vender(self.polo, 'USDT_BTC', nuevo_precio_venta_stop, float(self.rcb['BTC']['available']))
                    logger.debug('[stopLimit] Vendi!: ' + str(order))
                    if order:
                        self.precio_venta_stop = nuevo_precio_venta_stop
                        self.orden_venta_stop = int(order['orderNumber'])
                        if order['resultingTrades']:
                            amount_for = 0
                            for ord in order['resultingTrades']:
                                amount_for += float(ord['amount'])
                            if amount_for == float(self.rcb['BTC']['available']):
                                if self.tipo_rcb == 1:
                                    logger.debug('[stopLimit] Se vendieron todos los stopLimit, [precio_venta_stop: ' +
                                                 str(self.precio_venta_stop) + ']')
                                    break
                                else:
                                    logger.debug('[stopLimit] Se venden StopLimit pero el tipo_rcb es: '
                                                 + str(self.tipo_rcb))
                                    #corroborar esto
                                    self.rcb = returnCompleteBalances(self.polo)
                                    self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                                    self.dataFrame()
                            else:
                                logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                             'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                                self.no_loop()
                                self.rcb = returnCompleteBalances(self.polo)
                                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                                self.dataFrame()
                                continue
                        else:
                            logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                          'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                            self.no_loop()
                            self.rcb = returnCompleteBalances(self.polo)
                            self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                            self.dataFrame()
                            continue
                    else:
                        logger.debug('[stopLimit] No se ejecuto la orden de venta, vuelve a ejecutar')
                        self.no_loop()
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        self.dataFrame()
                        continue

                self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                for ord in self.roo:
                    if (ord['type'] == 'sell') and (self.orden_venta_stop == int(ord['orderNumber'])):
                        roo_stop = ord
                        break
                if roo_stop and self.tipo_rcb == 3:
                    logger.debug('[stopLimit] roo_stop and self.tipo_rcb == 3')
                    if self.precio_venta_stop <= self.valorVela:
                        logger.debug('[stopLimit] self.precio_venta_stop <= self.valorVela:, [precio_venta_stop: ' +
                                     str(self.precio_venta_stop) + '], [valorVela: ' + str(self.valorVela) + ']')
                        sleep(0.5)
                        self.no_loop()
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        self.dataFrame()
                        continue
                    else:
                        logger.debug('[stopLimit] ELSE => self.precio_venta_stop <= self.valorVela:, [precio_venta_stop: '
                                     + str(self.precio_venta_stop) + '], [valorVela: ' + str(self.valorVela))
                        nuevo_precio_venta_stop = calcularFloat(self.valorVela - (self.valorVela * 0.0001))

                    monto_total = float(roo_stop['amount']) + float(self.rcb['BTC']['available'])
                    valor_monto = calcularFloat(monto_total)
                    logger.debug('[stopLimit] moveOrder USDT_BTC: [orden_venta_stop: ' + str(self.orden_venta_stop) +
                                 '], [nuevo_precio_venta_stop: ' + str(nuevo_precio_venta_stop) + '], [valor_monto: '
                                 + str(valor_monto)+']')
                    order = moveOrder(self.polo, self.orden_venta_stop, nuevo_precio_venta_stop, valor_monto)
                    logger.debug('[stopLimit] Movi!: ' + str(order))
                    if order:
                        self.precio_venta_stop = nuevo_precio_venta_stop
                        self.orden_venta_stop = int(order['orderNumber'])
                        if order['resultingTrades']['USDT_BTC']:
                            amount_for = 0
                            for ord in order['resultingTrades']['USDT_BTC']:
                                amount_for += float(ord['amount'])
                            logger.debug('[stopLimit] if order[resultingTrades][USDT_BTC]:, [amount_for: '
                                         + str(amount_for) + '], [monto_total: ' + str(monto_total) + ']')
                            if amount_for == monto_total:
                                logger.debug('[stopLimit] Se vendieron todos los stopLimit, [precio_venta_stop: ' + str(
                                    self.precio_venta_stop) + ']')
                                break
                            else:
                                logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                              'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                                self.no_loop()
                                self.rcb = returnCompleteBalances(self.polo)
                                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                                self.dataFrame()
                                continue
                        else:
                            logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                          'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                            self.no_loop()
                            self.rcb = returnCompleteBalances(self.polo)
                            self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                            self.dataFrame()
                            continue
                    else:
                        logger.debug('[stopLimit] No se ejecuto la orden de moveOrder, vuelve a ejecutar')
                        self.no_loop()
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        self.dataFrame()
                        continue

                elif roo_stop and self.tipo_rcb == 2:
                    logger.debug('[stopLimit] roo_stop and self.tipo_rcb == 2')
                    if self.precio_venta_stop <= self.valorVela:
                        logger.debug('[stopLimit] self.precio_venta_stop <= self.valorVela:, [precio_venta_stop: ' + str(
                            self.precio_venta_stop) + '], [valorVela: ' + str(self.valorVela) + ']')
                        sleep(0.5)
                        self.no_loop()
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        self.dataFrame()
                        continue
                    else:
                        logger.debug('[stopLimit] ELSE => self.precio_venta_stop == 0:')
                        nuevo_precio_venta_stop = calcularFloat(self.valorVela - (self.valorVela * 0.0001))

                    logger.debug('[stopLimit] moveOrder USDT_BTC: [orden_venta_stop: ' + str(self.orden_venta_stop) +
                                 '], [nuevo_precio_venta_stop: ' + str(nuevo_precio_venta_stop) + ']')
                    order = moveOrder(self.polo, self.orden_venta_stop, nuevo_precio_venta_stop, False)
                    logger.debug('[stopLimit] Movi!: ' + str(order))
                    if order:
                        self.precio_venta_stop = nuevo_precio_venta_stop
                        self.orden_venta_stop = int(order['orderNumber'])
                        if order['resultingTrades']['USDT_BTC']:
                            amount_for = 0
                            for ord in order['resultingTrades']['USDT_BTC']:
                                amount_for += float(ord['amount'])
                            logger.debug('[stopLimit] if order[resultingTrades][USDT_BTC]:, [amount_for: ' + str(
                                         amount_for) + '], [BTC onOrders: ' + str(self.rcb['BTC']['onOrders']) + ']')
                            if amount_for == float(self.rcb['BTC']['onOrders']):
                                logger.debug('[stopLimit] Se vendieron todos los stopLimit, [precio_venta_stop: ' + str(
                                    self.precio_venta_stop) + ']')
                                break
                            else:
                                logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                              'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                                self.no_loop()
                                self.rcb = returnCompleteBalances(self.polo)
                                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                                self.dataFrame()
                                continue
                        else:
                            logger.debug('[stopLimit] No se vendio todo stopLimit, '
                                          'vuelve a ejecutar (orderNumber: ' + str(self.orden_venta_stop) + ')')
                            self.no_loop()
                            self.rcb = returnCompleteBalances(self.polo)
                            self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                            self.dataFrame()
                            continue
                    else:
                        logger.debug('[stopLimit] No se ejecuto la orden de moveOrder, vuelve a ejecutar')
                        self.no_loop()
                        self.rcb = returnCompleteBalances(self.polo)
                        self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                        self.dataFrame()
                        continue

                elif not roo_stop or self.tipo_rcb == 0:
                    logger.debug('[stopLimit] elif not roo_stop or self.tipo_rcb == 0:, Se vendieron todos los '
                                 'stopLimit, [precio_venta_stop: ' + str(self.precio_venta_stop) + ']')
                    break

                else:
                    logger.error('[stopLimit] ERROR!, ATENCION! no cayo en ningun if...')
                    logger.error('[stopLimit] tipo_rcb: ' + str(self.tipo_rcb) + ', roo_stop: ' + str(roo_stop))
                    self.no_loop()
                    self.rcb = returnCompleteBalances(self.polo)
                    self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                    self.dataFrame()
                    continue
            except Exception as err:
                logger.error('[stopLimit] ERROR! stopLimit se a caido, ' + str(err))
                self.no_loop()
                self.comprobar_en_proceso()
                if self.enProceso == 'compra':
                    self.dataFrame()
                    continue
                else:
                    sleep(1)
                    break

        self.count_loop = 0
        return 'stop_terminado'

    def bollinger_strat(self, df, targetcol='close'):
        """
            Metodo que calcula cuando dar senal de venta o compra
            los parametros son entregados en Self, excepto df
                - senal < 0 = senal de VENTA
                - senal > 0 = senal de COMPRA
        :param df: df
        :param valor_vela_size: index de la vela actual
        :param contador_bollinger_strat: Contador para comprobar que una vela supero al bbtop de forma excesiva
        :param contador_cantidad_bbbottom: contador que avisa cuando la vela es menor al bbbottom
        :return: senal
        """
        percent_contador = 0.00015
        valor_percent_contador = float(df['bbtop'].iloc[self.valor_vela_size]) + (float(df['bbtop'].iloc[self.valor_vela_size]) * percent_contador)

        #############################
        ####      REVISAR       #####
        ##############################

        # Comprueba si la vela supero al 'bbtop'
        if (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]):
            self.contador_bollinger_strat += 1
        #Si la vela bajo del bbtop (despues de haberlo superado), reinicia el contador y Vende
        if self.contador_bollinger_strat > 0 and self.enProceso == 'compra' and (
                df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]):
            self.contador_bollinger_strat, self.contador_cantidad_bbbottom = 0, 0
            senal = -1
            logger.debug('[bollinger_strat] SENAL Venta= '+str(senal)+', [valorVela: '+str(self.valorVela)+']')
            return senal
        elif self.contador_bollinger_strat == 0 and self.enProceso == 'compra' and (
                df['high'].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and(
                df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size] < valor_percent_contador):
            self.contador_bollinger_strat, self.contador_cantidad_bbbottom = 0, 0
            senal = -2
            logger.debug('[bollinger_strat] SENAL Venta= ' + str(senal) + ', [valorVela: ' + str(self.valorVela) + ']')
            return senal

        if df[targetcol].iloc[self.valor_vela_size] <= df['bbbottom'].iloc[self.valor_vela_size] or (
                df[targetcol].iloc[self.valor_vela_size] <= df['low'].iloc[self.valor_vela_size]) and (
                self.contador_cantidad_bbbottom == 0):
            self.contador_cantidad_bbbottom += 1
        elif self.contador_cantidad_bbbottom == 1 and (
                df[targetcol].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size] or
                df['low'].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size]) :
            self.contador_cantidad_bbbottom += 1
        elif self.valorVela > df['sma'].iloc[self.valor_vela_size] and self.contador_cantidad_bbbottom > 0:
            self.contador_cantidad_bbbottom = 0

        ####################333
        # ESTA WEA NO SIRVE
        ##################3
        """
        if (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] <= df['bbtop'].iloc[self.valor_vela_size - 1]) and (
                df[targetcol].iloc[self.valor_vela_size] < valor_venta) and(
                self.contador_bollinger_strat > 1 or self.contador_bollinger_strat == 0) and (
                self.contador_cantidad_bbtop > 1):
            senal = -2
            self.contador_bollinger_strat = 0
            self.contador_cantidad_bbtop = 0
            self.contador_cantidad_bbbottom = 0
            logger.debug('[bollinger_strat] SENAL Venta= ' + str(senal))
        

        if (df[targetcol].iloc[self.valor_vela_size] >= df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['bbtop'].iloc[self.valor_vela_size - 1] or
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['high'].iloc[self.valor_vela_size - 1]) and (
                df[targetcol].iloc[self.valor_vela_size] < valor_venta) and (
                self.contador_bollinger_strat > 1 or self.contador_bollinger_strat == 0) and (
                self.contador_cantidad_bbtop >= 1):
            #lo mas probable es que este caso no ocurra, pero se deja por precaucion
            senal = -3
            self.contador_bollinger_strat, self.contador_cantidad_bbtop, self.contador_cantidad_bbbottom  = 0, 0, 0
            logger.debug('[bollinger_strat] SENAL Venta= ' + str(senal)+', [valorVela: '+str(self.valorVela)+']')
        

        if (df[targetcol].iloc[self.valor_vela_size] < df['bbtop'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['bbtop'].iloc[self.valor_vela_size - 1] or
                df[targetcol].iloc[self.valor_vela_size - 1] >= df['high'].iloc[self.valor_vela_size - 1]):
            senal = -2
            self.contador_bollinger_strat, self.contador_cantidad_bbtop, self.contador_cantidad_bbbottom = 0, 0, 0
            logger.debug('[bollinger_strat] SENAL Venta= ' + str(senal)+', [valorVela: '+str(self.valorVela)+']')
        """

        #
        #   POSIBLE NUEVA VENTA, ACTUANDO CON EL HIGH... COMO LA COMPRA 2
        #
        if self.enProceso == 'hodl' and (
                df[targetcol].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size - 1] <= df['bbbottom'].iloc[self.valor_vela_size - 1] and
                self.contador_cantidad_bbbottom > 1) and (
                df[targetcol].iloc[self.valor_vela_size] < df['sma'].iloc[self.valor_vela_size]):
            self.contador_bollinger_strat, self.contador_cantidad_bbbottom = 0, 0
            senal = 1
            logger.debug('[bollinger_strat] SENAL Compra= ' + str(senal)+', [valorVela: '+str(self.valorVela)+']')

        elif self.enProceso == 'hodl' and (
                df['low'].iloc[self.valor_vela_size] <= df['bbbottom'].iloc[self.valor_vela_size]) and(
                df[targetcol].iloc[self.valor_vela_size] > df['bbbottom'].iloc[self.valor_vela_size]) and (
                df[targetcol].iloc[self.valor_vela_size] < df['sma'].iloc[self.valor_vela_size]):
            self.contador_bollinger_strat, self.contador_cantidad_bbbottom = 0, 0
            senal = 2
            logger.debug('[bollinger_strat] SENAL Compra= ' + str(senal) + ', [valorVela: ' + str(self.valorVela) + ']')

        else:
            senal = 0

        print(datetime.datetime.now(), ', Senal Hold = ', senal)
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
        while True:
            try:
                logger.debug('[comprobarVenta] Ingrese a comprobarVenta!')
                self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                if self.roo:
                    flag_for = True
                    for ord in self.roo:
                        if (ord['type'] == 'sell') and (self.orden_venta == int(ord['orderNumber'])):
                            self.dataFrame()
                            if self.precio_venta > self.valorVela:
                                logger.debug('[comprobarVenta] self.precio_venta > self.valorVela:, [precio_venta: '
                                             + str(self.precio_venta) + '], [valorVela: ' + str(self.valorVela) + ']')
                                nuevo_precio_venta = self.valorVela - (self.valorVela * 0.0001)
                                move = moveOrder(self.polo, self.orden_venta, nuevo_precio_venta, False)
                                if move:
                                    self.precio_venta = nuevo_precio_venta
                                    self.orden_venta = int(move['orderNumber'])
                                    if move['resultingTrades']['USDT_BTC']:
                                        amount_for = 0
                                        for ord2 in move['resultingTrades']['USDT_BTC']:
                                            amount_for += float(ord2['amount'])
                                        logger.debug('[comprobarVenta] if move[resultingTrades][USDT_BTC]:, [amount_for: '
                                                     + str(amount_for) + '], [amount: ' + str(ord['amount']) + ']')
                                        if amount_for == float(ord['amount']):
                                            logger.debug('[comprobarVenta] Se vende todo en BTC!, [precio_venta: '
                                                         + str(self.precio_venta) + ']')
                                            self.enProceso = 'hodl'
                                            self.stop, self.orden_venta_stop, self.orden_venta, self.precio_venta = 0, 0, 0, 0
                                            self.roo, self.tipo_rcb, self.rcb, flag_for = False, False, False, False
                                            self.precio_compra, self.orden_compra, self.precio_venta_stop = 0, 0, 0
                                            break
                                        else:
                                            logger.debug('[comprobarVenta] No se vende todo el BTC, se vuelve a comprobar')
                                            self.no_loop()
                                            break
                                    else:
                                        logger.debug('[comprobarVenta] No se vende todo el BTC, se vuelve a comprobar')
                                        self.no_loop()
                                        break
                                else:
                                    logger.error('[comprobarVenta] ERROR!, No se pudo mover '
                                                  'la orden para actualizar venta!, se repite el proceso')
                                    self.no_loop()
                                    break
                            else:
                                sleep(0.8)
                                logger.debug('[comprobarVenta] ELSE => self.precio_venta > self.valorVela:, [precio_venta: '
                                             + str(self.precio_venta)+'], [valorVela: '+str(self.valorVela)+']')
                                self.no_loop()
                                break

                        else:
                            logger.debug('[comprobarVenta] Se vende todo en BTC!, [precio_venta: '
                                         + str(self.precio_venta) + ']')
                            self.enProceso = 'hodl'
                            self.stop, self.orden_venta_stop, self.orden_venta, self.precio_venta = 0, 0, 0, 0
                            self.roo, self.tipo_rcb, self.rcb, flag_for  = False, False, False, False
                            self.precio_compra, self.orden_compra, self.precio_venta_stop = 0, 0, 0
                            break

                    if not flag_for:
                        break
                else:
                    logger.debug('[comprobarVenta] Se vende todo en BTC!, [precio_venta: ' + str(self.precio_venta) + ']')
                    self.enProceso = 'hodl'
                    self.stop, self.orden_venta_stop, self.orden_venta, self.precio_venta = 0, 0, 0, 0
                    self.roo, self.tipo_rcb, self.rcb = False, False, False
                    self.precio_compra, self.orden_compra, self.precio_venta_stop = 0, 0, 0
                    break
            except Exception as err:
                logger.error('[comprobarVenta] ERROR! comprobarVenta se a caido, ' + str(err))
                self.no_loop()
                self.rcb = returnCompleteBalances(self.polo)
                self.tipo_rcb = procesarRCB(self.rcb, 'BTC')
                if self.tipo_rcb == 2 or self.tipo_rcb == 3:
                    continue
                else:
                    sleep(1)
                    break

        self.count_loop = 0

    def comprobarCompra(self):
        """
            Metodo que acelera y asegura la venta, solo si valorVela no es menor a bbbottom
        :param precio_compra: Precio al cual fue Comprado la divisa
        :param valorVela: Valor actual de la vela
        :param orden_compra: Numero de orden de Compra
        :param polo: api Poloniex (self.polo)
        :return:
        """
        while True:
            try:
                logger.debug('[comprobarCompra] Ingrese a comprobarCompra!')
                self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
                ###############
                #   DUMMY     #
                ###############
                """
                number = int(self.roo[0]['orderNumber'])
                self.precio_compra = float(7300.00000001)
                move = moveOrder(self.polo, number, self.precio_compra, False)
                print(move)
                print('ya ql')
                """
                if self.roo:
                    flag_for = True
                    for ord in self.roo:
                        if (ord['type'] == 'buy') and (self.orden_compra == int(ord['orderNumber'])):
                            df = self.dataFrame()
                            if (self.precio_compra < self.valorVela) and (
                                    self.valorVela > df['bbbottom'].iloc[self.valor_vela_size]):
                                pass
                                #logger.error('[comprobarCompra] ERROR! ATENCION!, '
                                #              'OCURRIO UN ERROR QUE NO SE A VALIDADO!!, REALIZAR OTRA LOGICA')

                            #GENERAR VALIDACION QUE SI VALORVELA < bbbottom NO COMPRE Y DEJE GUARDADO EL MONTO QUE LE QUEDA POR COMPRAR, SIGA SU FLUJO NORMAL
                            #SI EL VALOR VUELVE A SUBIR QUE COMPRE SOLO ESE MONTO RESTANTE, SI SE VA A PERDIDA QUE CANCELE LA ORDEN
                            if self.precio_compra < self.valorVela:
                                nuevo_precio_compra = calcularFloat(self.valorVela + (self.valorVela * 0.0001))
                                logger.debug('[comprobarCompra] self.precio_compra < self.valorVela:, '
                                             '[precio_compra: ' + str(self.precio_compra) + '], [valorVela: '
                                             + str(self.valorVela) + '], [nuevo_precio_compra: '+str(nuevo_precio_compra)+']')
                                monto_btc = float(ord['amount'])
                                logger.debug('[comprobarCompra] monto_btc: ' + str(monto_btc))
                                monto_usdt_nuevo = calcularFloat(monto_btc * nuevo_precio_compra)
                                logger.debug('[comprobarCompra] monto_usdt_nuevo: ' + str(monto_usdt_nuevo))
                                self.rcb = returnCompleteBalances(self.polo)
                                suma_usdt = float(self.rcb['USDT']['available']) + float(self.rcb['USDT']['onOrders'])
                                if suma_usdt >= monto_usdt_nuevo:
                                    logger.debug('[comprobarCompra] if suma_usdt >= monto_usdt_nuevo:, [suma_usdt: '
                                                 + str(suma_usdt) + ']')
                                    move = moveOrder(self.polo, self.orden_compra, nuevo_precio_compra, False)
                                else:
                                    #######
                                    #Poner atencion aca!
                                    #######
                                    valor_monto_nuevo = calcular_monto(suma_usdt, nuevo_precio_compra)
                                    logger.debug('[comprobarCompra] ELSE => suma_usdt >= monto_usdt_nuevo:, [suma_usdt: ' +
                                                 str(suma_usdt) + '], [valor_monto_nuevo: ' + str(valor_monto_nuevo) + ']')
                                    logger.debug('[comprobarCompra] [valor_monto_nuevo * nuevo_precio_compra: ' +
                                                 str(valor_monto_nuevo*nuevo_precio_compra)+']')
                                    move = moveOrder(self.polo, self.orden_compra, nuevo_precio_compra, valor_monto_nuevo)

                                logger.debug('[comprobarCompra] Mover!: ' + str(move))
                                if move:
                                    self.precio_compra = nuevo_precio_compra
                                    self.orden_compra = int(move['orderNumber'])
                                    if move['resultingTrades']['USDT_BTC']:
                                        amount_for = 0
                                        for ord in move['resultingTrades']['USDT_BTC']:
                                            amount_for += float(ord['amount'])
                                        logger.debug('[comprobarCompra] if move[resultingTrades][USDT_BTC]:, [amount_for: '
                                                     +str(amount_for)+'], [monto_btc: '+str(monto_btc)+']')
                                        if amount_for == monto_btc:
                                            logger.debug('[comprobarCompra] comprobarCompra = True, [precio_compra: ' +
                                                         str(self.precio_compra)+']')
                                            self.enProceso = 'compra'
                                            flag_for = False
                                            break
                                        else:
                                            logger.debug('[comprobarCompra] '
                                                          'No se compra todo el BTC, se vuelve a comprobar')
                                            self.no_loop()
                                            break
                                    else:
                                        logger.debug('[comprobarCompra] No se compra todo el BTC, se vuelve a comprobar')
                                        self.no_loop()
                                        break
                                else:
                                    logger.error('[comprobarCompra] ERROR!, No se '
                                                  'pudo mover la orden para actualizar Compra!, se repite el proceso')
                                    self.no_loop()
                                    break
                            else:
                                logger.debug('[comprobarCompra] ELSE => self.precio_compra < self.valorVela:, '
                                             '[precio_compra: '+str(self.precio_compra)+'], [valorVela: '
                                             + str(self.valorVela)+']')
                                sleep(1)
                                self.no_loop()
                                break
                        else:
                            logger.debug('[comprobarCompra] ELSE => (ord[type] == buy) and (self.orden_compra == '
                                         'int(ord[orderNumber])):, [precio_compra: '+str(self.precio_compra)+']')
                            self.enProceso = 'compra'
                            flag_for = False
                            break

                    if not flag_for:
                        break
                else:
                    logger.debug('[comprobarCompra] ELSE => if self.roo:, [precio_compra: '+str(self.precio_compra)+']')
                    self.enProceso = 'compra'
                    break
            except Exception as err:
                logger.error('[comprobarCompra] Error Inesperado, ATENCION! REVISAR! '+str(err))
                self.no_loop()
                self.rcb = returnCompleteBalances(self.polo)
                self.tipo_rcb = procesarRCB(self.rcb, 'USDT')
                if self.tipo_rcb == 2 or self.tipo_rcb == 3:
                    continue
                else:
                    sleep(1)
                    break

        self.count_loop = 0

    def ejecuta(self):
        """
            Demonio que ejecuta infinitamente el Bot
        :return:
        """
        logger.info('[ejecuta] Inicie Demonio Ejecuta')
        while True:
            try:
                df = self.dataFrame()
                self.whaleBot(df)
                if datetime.datetime.today() > self.date3hour:
                    self.__del__()
                    self.date3hour = datetime.datetime.today() + datetime.timedelta(hours=3)
                    sleep(1)
                self.reboot()
            except Exception as err:
                logger.error('[ejecuta] Error!, vuelve a ejecutar!, '+str(err))
                self.no_loop()
                sleep(0.7)
                continue
            self.count_loop = 0

    def __del__(self):
        logger.debug('[__del__] Objetos destruidos')
        print(datetime.datetime.now(), ' Objetos destruidos')


if __name__ == '__main__':
    import logging.handlers
    #logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    #HANDLER PARA CONSOLA
    #handler = logging.handlers.TimedRotatingFileHandler(filename='examples/chart/logs_dummy/ChartDummy.log', when="h", interval=8,
    #                                                    backupCount=50)
    #HANDLER PARA PYCHARM
    handler = logging.handlers.TimedRotatingFileHandler(filename='logs_dummy/ChartDummy.log', when="h", interval=16,
                                                        backupCount=50)
    formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    IniciaChart()
    # print(df.tail(7)[['open', 'close', 'percentChange', 'sma','emaslow', 'emafast', 'macd', 'bbtop', 'bbbottom', 'bbrange', 'bbpercent']])
    #print('df tail: ', df.tail(60)[['close', 'sma', 'bbtop', 'bbbottom']])
    #tail = df.tail(51)['close']
    #print('trail size: ', df.tail(51)['sma'].size)
    #print('trail size2: ', df['sma'].size)
    #print('trail size3: ', df['sma'].size - 1)
    #tail2 = df.tail(120)['close']
