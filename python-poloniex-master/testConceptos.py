import logging
import time
import datetime


def calcularStop():
    print('holaaaa')
    otroCalcula()
    print('termine')


def otroCalcula():
    print('hola 2')


class OtraClase(object):
    def __init__(self):
        ClasePrueba().ejecuta()

    def no_loop(self):
        """
            Metodo que comprueba que el Bot no quede en un loop infinito
        :return:
        """
        if self.count_loop > self.max_loop:
            self.__del__()
            ClasePrueba().ejecuta()

    def __del__(self):
        print(datetime.datetime.now(), ' Objetos destruidos')


class ClasePrueba(OtraClase):
    def __init__(self):
        print('inicie clase 1')
        self.valor1 = 1
        self.val_1 = 0
        self.count_loop = 0
        self.max_loop = 5
        print('valor 1: ', self.valor1)
        self.valor2 = self.valor1 + 3333
        print('valor 2: ', self.valor2)

    def calculadora(self):
        try:
            #super().__init__()
            calcularStop()
            bool_while = True
            cont = 0
            while bool_while:
                if cont < 4:
                    print('if!, cont: ', cont)
                    cont += 1
                else:
                    bool_while = False
                    print('else!, cont: ', cont)
            print('sali del while')
            self.valor3 = self.valor2 + 5
            print('valor 3: ', self.valor3)
            self.valor2 = self.valor2 + self.valor3
            print('valor 2 y 3 sumados: ', self.valor2)
            i = 0,1
            self.printPantalla()
            print('ya imprimi!')

            self.count_loop += 1
            self.no_loop()
            self.val_1 += 1
            while self.val_1 < 3:
                self.calculadora()
            #for x in i:
             #   print('aca se va a caer')
              #  print(i[4])
        except Exception as err:
            print('err: ', str(err))
            self.valor2 = 0
            print('valor2: ', self.valor2)

        #finally:
        #    self.count_loop = 0

    def printPantalla(self):
        try:
            print('print a self valor 1: ', self.valor1)
            cas = 'qwe'+ 123
        except:
            print('printPantalla error!')
            self.valor2 = 1
            print('valor2: ', self.valor2)

    def metodoQueRetorna(self):
        print('hola vengo a retornar')
        return 'hola'

    def ejecuta(self):
        print('entre al ejecuta')
        try:
            qwe = True
            while qwe:
                self.calculadora()
                valor = 2
                valor_otro = int(valor)
                self.metodoQueRetorna()
                print('valor otro: ', valor_otro)
                qwe = False
                """
                if valor ==2:
                    self.ejecuta()
                else:
                    print('error!, no cai')
                """
        except Exception as err:
            print('error!, vuelve a ejecutar!', str(err))
            self.valor2 = 4
            print('valor2: ', self.valor2)
            self.ejecuta()

        print('sali del while')



if __name__ == '__main__':
    logging.basicConfig(filename='testConceptos.log', level=logging.DEBUG)
    logging.getLogger(__name__)
    val= 10320
    val2= val -(val * 0.0024)
    logging.debug('val ='+str(val))
    print('val 1: ',val,'. val 2: ', val2)
    print('Hora: ' + (str(time.strftime("%H:%M:%S"))))
    print('datetime: ', datetime.datetime.now())
    logging.debug(datetime.datetime.now())
    #list = [['orderNumber': '173383558034'], {'resultingTrades': {'amount': '0.00336478', 'date': '2018-03-16 19:40:22', 'rate': '620.54335800', 'total': '2.08799188', 'tradeID': '8459436', 'type': 'sell'}}]
    #val = list['resultingTrades']['amount']
    ordenes = {'orderNumber': '173383558034', 'resultingTrades': [{'amount': '0.00336478', 'date': '2018-03-16 19:40:22', 'rate': '620.54335800', 'total': '2.08799188', 'tradeID': '8459436', 'type': 'sell'}]}
    order_number = int(ordenes['orderNumber'])
    today = datetime.date.today()
    print('today: ', str(today))
    asd = 1
    if asd != 1:
        print('no es igual a 1')
    if (asd != 2) and(
            asd != 3) and(
            asd != 4) and(
            asd != 5):
        print('no es igual a 2')
    if asd == 1:
        print('valo 1')
        asd += 1
    elif asd == 2:
        print('valo 2')
        asd += 1
    elif asd == 3:
        print('valo 3')
        asd += 1
    else:
        print('valo no se k wea')
    print('-------------------------------')
    valor = 1

    while True:
        if valor ==0:
            valor += 1
            print('valor 0')
        elif valor ==1:
            print('valor 1')
            valor += 1
        elif valor == 2:
            print('valor 2')
            valor += 1
            if valor == 3:
                print('nuevo 3')
                valor += 1
                if valor == 4:
                    print('nuevo 4')
                    valor += 2
                    if valor == 5:
                        print('nuevo 5')
                    else:
                        num = [1,2,3,4,5,6]
                        for i in num:
                            print('valor i!: ', i)
                            if i == 3:
                                break

                        print('continue')
                        break
                    if valor == 5:
                        print('pase por aqui')
            print('print lalalalla')
        elif valor == 3:
            print('valor 3')
            valor += 1
            break
        elif valor == 4:
            print('valor 4')
            valor += 1
        elif valor == 5:
            print('valor 5')
            valor += 1
        else:
            print('otro valor: ', valor)
            valor += 9999999
            break


    print('valor de valor xd: ', valor)
    #funciona con true, con valores o cadena string
    val_v="asdasd"
    #funciona con False, cero y espacios en blanco
    val_f= ""
    if val_v:
        print('valor v')
    if not val_f:
        print('valor f')



    order = ['asd', 1]
    print(order[0])
    print(order[1])
    OtraClase()
