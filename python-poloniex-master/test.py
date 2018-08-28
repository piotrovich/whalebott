import poloniex
import unittest
import requests
import logging

class TestPolo(object):
    def __init__(self, **kwargs):
        print('clase iniciada')

    def vender(self):
        self.roo = returnOpenOrders(self.polo, 'USDT_BTC')
        if self.roo:
            for ord in self.roo:
                if (ord['type'] == 'sell') and (self.orden_venta == int(ord['orderNumber'])) and (
                        self.precio_venta > self.valorVela):
                    self.contador_venta += 1
                    move = moveOrder(self.polo, self.orden_venta, self.valorVela, False)
                    if move:
                        self.orden_venta = int(order['orderNumber'])
                        self.precio_venta = self.valorVela
                        self.dataFrame()
                        self.vender()
                    else:
                        logging.error(
                            '[botWhale] ERROR!, No se pudo mover la orden para actualizar venta!, se repite el proceso')
                        self.vender()
                else:
                    logging.debug('[botWhale] Mantener en Venta')
                    return 'break'

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
            logging.debug('[botWhale] Se vende todo en BTC!')
            return 'break'



if __name__ == '__main__':

    print('antes del for')
    for i in range(10):
        if i == 5:
            continue
        print('nuero: ',i)



    #unittest.main()
