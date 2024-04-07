#modo 0 ap modo 1 conectarse a una red
modo=0
frecuenciaDeMuestreoMinutos=1
pinData=21
pinClock=34
pinDataDos=18
pinClockDos=33

import socket
import network
import utime
from machine import Timer, Pin
from machine import I2C

import esp
esp.osdebug(None)

import gc
gc.collect()

from claseLedOnBoard import LedOnBoard
led = LedOnBoard(pinNum=15)

from claseAHT15 import AHT15
i2c = I2C(0,scl=Pin(pinClock), sda=Pin(pinData),freq=25000)
sensor = AHT15(i2c)
i2cDos= I2C(1,scl=Pin(pinClockDos), sda=Pin(pinDataDos),freq=25000)
sensorDos = AHT15(i2cDos)

sensor_list=[sensor,sensorDos]





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
    station.config(ssid='prueba')  # Configura el SSID del punto de acceso
    station.config(max_clients=10)  # Establece cuántos clientes pueden conectarse a la red
    station.active(True)  # Activa la interfaz
    print('AP encendido')
    led.parpadeo(3)
    with open('ifconfig.txt', 'w') as f:
        f.write(str(station.ifconfig()))  # Guarda la información en un archivo

print("http://" + station.ifconfig()[0])


with open('ifconfig.txt', 'w') as f:
    f.write(str(station.ifconfig()))  # Guarda la información en un archivo

def strftime(sample_time):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return "{:02d} {} {:04d} {:02d}:{:02d}:{:02d}".format(sample_time[2], months[sample_time[1] - 1], sample_time[0], sample_time[3], sample_time[4], sample_time[5])


def cargarIndex(sensor_data_list):
    with open('index.html', 'r') as f:
        html = f.read()
    
    for i, sensor_data in enumerate(sensor_data_list):
        temperature, humidity, date = sensor_data
        html = html.replace('{{ temperature{0} }}'.format(i), str(temperature))
        html = html.replace('{{ humidity{0} }}'.format(i), str(humidity))
        html = html.replace('{{ date{0} }}'.format(i), strftime("%Y-%m-%d %H:%M:%S", date))
    
    return html

       
def guardarCsv(sensor_data_list):
    try:
        with open('datos_adc.csv', 'a') as f:
            for data in sensor_data_list:
                # Imprimir los datos en la consola
                print("Datos tomados:", data[0], "°C,", data[1], "%, tiempo:", strftime("%Y-%m-%d %H:%M:%S", data[2]))
                f.write("{},{},{}".format(data[0], data[1], strftime("%Y-%m-%d %H:%M:%S", data[2]))+',')  # Escribir el elemento seguido de una coma
            f.write('\n')  # Nueva línea para el siguiente conjunto de datos
        led.parpadeo()
    except OSError:
        print('Error al guardar en el archivo CSV')


def tomarDatos(sensor_list):
    sensor_data_list = []
    for sensor in sensor_list:
        temperature, humidity = sensor.readRensor()
        sensor_data_list.append((temperature, humidity, utime.localtime()))
    return sensor_data_list

def my_callback(timer):
    guardarCsv(tomarDatos(sensor_list))
    
def minutos2Milisegundos(minutos):
    # Se multiplica el número de minutos por el número de milisegundos en un minuto (60 segundos = 60000 milisegundos)
    return minutos * 60000




# Configuración del temporizador periódico que se activa cada minuto
tim = Timer(-1)
tim.init(period=minutos2Milisegundos(frecuenciaDeMuestreoMinutos), mode=Timer.PERIODIC, callback=my_callback)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)


while True:
    conexion, direccion = s.accept()
    request = conexion.recv(1024)
    sensor_data_list = tomarDatos(sensor_list)
    
    if 'GET /download/csv' in request.decode('utf-8'):
        conexion.send('HTTP/1.1 200 OK\n')
        conexion.send('Content-Type: text/csv\n')
        conexion.send('Content-Disposition: attachment; filename=datos_adc.csv\n')
        conexion.send('Connection: close\n\n')
        with open('datos_adc.csv', 'rb') as f:
            conexion.sendall(f.read())
    else:
        respuesta = cargarIndex(sensor_data_list)
        conexion.send('HTTP/1.1 200 OK\n')
        conexion.send('Content-Type: text/html\n')
        conexion.send('Connection: close\n\n')
        conexion.sendall(respuesta)
        
    conexion.close()




