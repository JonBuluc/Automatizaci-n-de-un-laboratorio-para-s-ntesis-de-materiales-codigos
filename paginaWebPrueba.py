try:
    import usocket as socket
except:
    import socket

import network
import esp
esp.osdebug(None)

import gc
gc.collect()

modo = 0

if modo == 1:
    ssid = 'Xiaomi 12X'
    password = '318345641'

    station = network.WLAN(network.STA_IF)

    station.active(True)
    station.connect(ssid, password)

    while not station.isconnected():
        pass

    print('Conexion correcta')
    with open('ifconfig.txt', 'w') as f:
        f.write(str(station.ifconfig()))  # Guarda la información en un archivo

else:
    station = network.WLAN(network.AP_IF)  # Crea la interfaz del punto de acceso
    station.config(ssid='Medidor Temp y Hum')  # Configura el SSID del punto de acceso
    station.config(max_clients=10)  # Establece cuántos clientes pueden conectarse a la red
    station.active(True)  # Activa la interfaz
    print('AP encendido')
    with open('ifconfig.txt', 'w') as f:
        f.write(str(station.ifconfig()))  # Guarda la información en un archivo

print("http://" + station.ifconfig()[0])


def pagina_web():
    html = """<!DOCTYPE html>
    <html>
    <head><title>Página de Ejemplo</title></head>
    <body>
    <h1>Hola desde tu ESP32!</h1>
    <p>¡Esta es una página de ejemplo!</p>
    </body>
    </html>"""
    return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conexion, direccion = s.accept()
    request = conexion.recv(1024)
    respuesta = pagina_web()
    conexion.send('HTTP/1.1 200 OK\n')
    conexion.send('Content-Type: text/html\n')
    conexion.send('Connection: close\n\n')
    conexion.sendall(respuesta)
    conexion.close()
