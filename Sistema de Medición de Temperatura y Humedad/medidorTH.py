#modo 0 ap modo 1 conectarse a una red
modo=0
frecuenciaDeMuestreoMinutos=10
pinData=38
pinClock=40
pinDataDos=37
pinClockDos=39

import socket
import network
import time
from machine import Timer, Pin
from machine import I2C
import esp
esp.osdebug(None)

import os

import gc
gc.collect()

from claseLedOnBoard import LedOnBoard
led = LedOnBoard(pinNum=15)

from claseAHT15 import AHT15

i2c = I2C(0,scl=Pin(pinClock), sda=Pin(pinData),freq=25000)
sensor = AHT15(i2c)
i2cDos= I2C(1,scl=Pin(pinClockDos), sda=Pin(pinDataDos),freq=25000)
sensorDos = AHT15(i2cDos)


sensorList=[sensor,sensorDos]

from machine import UART
uart = UART(0, baudrate=9600, tx=2, rx=1)

pin4 = Pin(4, Pin.OUT)
pin4.on()

# Función para decodificar los elementos recibidos
def decodeElements(data):        
    elements = data.split(b'#')
    try:
        decodedElements = [float(element) for element in elements if element]
    except:
        decodedElements=[element for element in elements if element]
    #en la expresion regular se debe de verificar si el if es necesario
    decodedElements = [float(element) for element in elements if element]
    return decodedElements



if modo == 1:
    ssid = 'Xiaomi 12X'
    password = '318345641'

    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)

    while not station.isconnected():
        pass

    print('Conexion correcta')
    led.parpadeo(3)
    with open('ifconfig.txt', 'w') as f:
        f.write(str(station.ifconfig()))  # Guarda la información en un archivo

else:
    station = network.WLAN(network.AP_IF)  # Crea la interfaz del punto de acceso
    station.config(ssid='Medidor Temp y humedad')  # Configura el SSID del punto de acceso
    station.config(max_clients=10)  # Establece cuántos clientes pueden conectarse a la red
    station.active(True)  # Activa la interfaz
    print('AP encendido')
    led.parpadeo(3)
    with open('ifconfig.txt', 'w') as f:
        f.write(str(station.ifconfig()))  # Guarda la información en un archivo

print("http://" + station.ifconfig()[0])


def strftime(sampleTime):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return "{:02d} {} {:04d} {:02d}:{:02d}:{:02d}".format(sampleTime[2], months[sampleTime[1] - 1], sampleTime[0], sampleTime[3], sampleTime[4], sampleTime[5])


def cargarIndex(sensorDataList):
    with open('index.html', 'r') as f:
        html = f.read()
    
    for i, sensorData in enumerate(sensorDataList):
        temperature, humidity, date = sensorData
        html = html.replace('{{ temperature{0} }}'.format(i), str(temperature))
        html = html.replace('{{ humidity{0} }}'.format(i), str(humidity))
        html = html.replace('{{ date{0} }}'.format(i), strftime(date))
    
    return html

       
def guardarCsv(sensorDataList):
    try:
        with open('datos.csv', 'a') as f:
            for data in sensorDataList:
                # Imprimir los datos en la consola
                print("Datos tomados:", data[0], "°C,", data[1], "%, tiempo:", strftime("%Y-%m-%d %H:%M:%S", data[2]))
                f.write("{},{},{}".format(data[0], data[1], strftime("%Y-%m-%d %H:%M:%S", data[2]))+',')  # Escribir el elemento seguido de una coma
            f.write('\n')  # Nueva línea para el siguiente conjunto de datos
        led.parpadeo()
    except OSError:
        print('Error al guardar en el archivo CSV')


def tomarDatos(sensorList):
    sensorDataList = []
    for sensor in sensorList:
        temperature, humidity = sensor.readSensor()
        count=0
        while temperature == "no data":
            time.sleep(0.1)
            temperature, humidity = sensor.readSensor()
            count+=1
            if count==10:
                break

        
        datosMuestra=(temperature,humidity,time.localtime())
        sensorDataList.append(datosMuestra)

    decodedElements=receiveDataMicroExt(uart)
    
    sensorDataList.append((decodedElements[0],decodedElements[1],time.localtime()))
    sensorDataList.append((decodedElements[2],decodedElements[3],time.localtime()))
    
    return sensorDataList

def my_callback(timer):
    guardarCsv(tomarDatos(sensorList))
    
def minutos2Milisegundos(minutos):
    # Se multiplica el número de minutos por el número de milisegundos en un minuto (60 segundos = 60000 milisegundos)
    return minutos * 60000

def receiveDataMicroExt(uart,pinEstimulacion):
    pinEstimulacion.off()  # Bajar el pin 4
    
    while uart.any() < 4:  # no se si es necesario el menor 4
        pass
    
    # Leer datos recibidos
    receivedData = uart.read()  # Leer 4 elementos
    
    # Decodificar y mostrar los elementos recibidos
    decodedElements = decodeElements(receivedData)
    
    pinEstimulacion.on()  # Levantar el pin 4

    #recibe n numero de datos pero debes de conocer lo que se envia,
    #Se puede hacer mas especifico o se puede hacer otra funcion que lo ordene
    #por ejemplo en un diccionario
    
    return decodedElements




# Configuración del temporizador periódico que se activa cada minuto
tim = Timer(-1)
tim.init(period=minutos2Milisegundos(frecuenciaDeMuestreoMinutos), mode=Timer.PERIODIC, callback=my_callback)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


while True:
    conexion, direccion = s.accept()
    request = conexion.recv(1024)
    sensorDataList = tomarDatos(sensorList)

    
    if 'GET /download/csv' in request.decode('utf-8'):
        conexion.send('HTTP/1.1 200 OK\n')
        conexion.send('Content-Type: text/csv\n')
        conexion.send('Content-Disposition: attachment; filename=datos.csv\n')
        conexion.send('Connection: close\n\n')
        try:
            with open('datos.csv', 'rb') as f:
                conexion.sendall(f.read())
        except:
            pass

    elif 'POST /delete/csv' in request.decode('utf-8'):
        # Eliminar el archivo CSV
        try:
            os.remove('datos.csv')
        except:
            pass
        # Respuesta al cliente
        conexion.send('HTTP/1.1 200 OK\n')
        conexion.send('Content-Type: text/html\n')
        conexion.send('Connection: close\n\n')
        conexion.sendall('<html><body><h1>Archivo CSV borrado exitosamente.</h1></body></html>')

    else:
        respuesta = cargarIndex(sensorDataList)
        conexion.send('HTTP/1.1 200 OK\n')
        conexion.send('Content-Type: text/html\n')
        conexion.send('Connection: close\n\n')
        conexion.sendall(respuesta)
        
    conexion.close()


