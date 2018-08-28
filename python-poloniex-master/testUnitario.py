import datetime


def multiple(valor, multiple):
    return True if valor % multiple == 0 else False


def metodo(count):
    try:
        monto = 2.98132349
        nuevo_monto = monto + (monto * 0.0025)
        print(nuevo_monto)
        str_1= 'asdqwe'
        int_1 = 123
        val = (str_1 + int_1) * 4 + 'asd'
        print('funciono!')

    except Exception as err:
        print('Error!', str(err))
        count += 1
        if count < 2:
            metodo(count)
        else:
            count = 0
    finally:
        print('lo sabia!!!: ', count)
        print('llamar a ChartDummy(api, USDT_BTC).ejecuta()!')

count = 0
metodo(count)
print('asdasd')


try:
    valor_monto = ((6876 * 100) / 0.002) / 100
    print(valor_monto)
    fecha_nueva = str('2018-04-04 10:16:01')
    hoy = datetime.datetime.today()
    fecha2 = hoy - datetime.timedelta(days=1) #minutes
    date1hour = hoy + datetime.timedelta(hours =1)
    print('hoy: ', hoy)
    formato1 = "%d-%m-%y %I:%m %p"
    formato2 = "%a %b %d %H:%M:%S %Y"
    formato3 = '%Y-%m-%d %H:%M:%S'
    cadena1 = hoy.strftime(formato1)
    cadena2 = hoy.strftime(formato2)
    print('cadena1: ', cadena1)
    print('cadena2: ', cadena2)
    str_to_date = datetime.datetime.strptime(fecha_nueva, formato3)
    print('str_to_date: ', str(str_to_date))

    #for d in range(hoy - fecha2).days

    fecha_nueva2 = str('2018-04-04 10:16:01')
    numero = fecha_nueva2[15:16]
    print(numero)
    arreglo1 = [0,1,2,3,4]
    if numero in arreglo1:
        print('wena')
        nuevo_numero = fecha_nueva2[:15] + '0:00'
    else:
        print('wena2')
        nuevo_numero = fecha_nueva2[:15] + '5:00'
    print('nuevo_numero: ', nuevo_numero)

    """
                            otra_fecha = df.index

        fecha = df.iloc[self.valor_vela_size].name
        fecha2 = fecha + datetime.timedelta(seconds=59, milliseconds=999, minutes=4)
        fecha_nueva_str= str('2018-04-04 10:16:01')
        format = '%Y-%m-%d %H:%M:%S'
        fecha_nueva_date = datetime.datetime.strptime(fecha_nueva_str, format)
        
        
                            numero = compra_date[15:16]
                            arreglo1 = [0, 1, 2, 3, 4]
                            if numero in arreglo1:
                                nuevo_numero = compra_date[:15] + '0:00'
                            else:
                                nuevo_numero = compra_date[:15] + '5:00'
                            format = '%Y-%m-%d %H:%M:%S'
                            fecha_nueva_date = datetime.datetime.strptime(nuevo_numero, format)
                            count = 0
                            df_nuevo = False
                            if fecha_nueva_date in df.index:
                                for num in df.index:
                                    count += 1
                                    if num == fecha_nueva_date:
                                        df_nuevo = df.iloc[count-1]
                                        break
                            """


    val=  0.0024
    val_usd = 7292.7292
    stop = val_usd - (val_usd * val)
    print('stop: ', stop)


except Exception as err:
    print('Error, ', str(err))


