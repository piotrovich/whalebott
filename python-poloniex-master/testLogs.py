import datetime
import logging
import time
import logging.handlers

def metodo_log():
    try:
        import logging.handlers

        logging.basicConfig(level=logging.DEBUG)

        # Creamos una instancia al logger con el nombre especificado
        logger = logging.getLogger('prueba')

        # Indicamos el nivel máximo de seguridad para los mensajes que queremos que se
        # guarden en el archivo de logs
        # Los niveles son:
        #   DEBUG - El nivel mas alto
        #   INFO
        #   WARNING
        #   ERROR
        #   CRITIAL - El nivel mas bajo
        logger.setLevel(logging.DEBUG)



        # Creamos una instancia de logging.handlers, en la cual vamos a definir el nombre
        # de los archivos, la rotación que va a tener, y el formato del mismo

        # when - determina cada cuando se rota el archivo:
        #   'S' Seconds
        #   'M' Minutes
        #   'H' Hours
        #   'D' Days
        #   'W' Week day (0=Monday)
        #   'midnight'  Roll over at midnight
        # interval - determina el intervalo, por ejemplo si indicamos minutos, interval
        # equivale al numero de minutos.
        # Si backupCount=0, no eliminara ningún fichero rotado
        handler = logging.handlers.TimedRotatingFileHandler(filename='testLog/file.log', when="s", interval=3, backupCount=5)

        # Definimos el formato del contenido del archivo de logs
        formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Añadimos el formato al manejador
        handler.setFormatter(formatter)

        # Añadimos el manejador a nuestro logging
        logger.addHandler(handler)

        while True:
            # Añadimos mensajes al fichero de log
            logger.debug('message debug')
            logger.info('message info')
            logger.warning('message warning')
            logger.error('message error')
            logger.critical('message critical')
            print('acabo de logear', datetime.datetime.now())
            time.sleep(1)


    except Exception as err:
        print('ERROR! ', str(err))
        metodo_log()


if __name__ == '__main__':
    metodo_log()



