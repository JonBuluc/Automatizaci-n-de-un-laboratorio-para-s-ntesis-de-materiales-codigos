from machine import Pin
# esto es en particular para alimentar el sensor por los pines 17 o 16
# Configurar el pin GPIO 17 como salida
pinout = Pin(17, Pin.OUT)
pinOutDos=Pin(16,Pin.OUT)

# Encender el pin
pinout.on()
print("17 on")
pinOutDos.on()
print("16 on")


from machine import I2C
import time

class AHT15:
    def __init__(self, i2c, address=0x38):
        """
        Inicializa la clase AHT15.

        Parámetros:
        - i2c: Objeto I2C que se utilizará para la comunicación.
        - address: Dirección del sensor en el bus I2C (por defecto: 0x38).
        """
        self.i2c = i2c  # Asigna el objeto I2C para la comunicación
        self.address = address  # Asigna la dirección del sensor
        self.conectado = False  # Indica si se ha establecido conexión con el sensor
        
        # Intenta establecer conexión con el sensor al inicializar la instancia
        self.conectarse()

    def readSensor(self):
        """
        Lee los datos de temperatura y humedad del sensor AHT15.

        Retorna:
        - temperature: Temperatura en grados Celsius.
        - humidity: Humedad relativa en porcentaje.
        """
        if self.conectado:
            pass
        else:
            # Intentar reconectar si no hay conexión
            self.conectarse()

        try:
            # Enviar comando de inicio de medición
            self.i2c.writeto(self.address, bytes([0xAC, 0x33, 0x00]))

            # Esperar que la medición esté lista (aproximadamente 80 ms)
            time.sleep_ms(80)

            # Leer datos de temperatura y humedad del sensor
            data = self.i2c.readfrom(self.address, 6)
            
            # Calcular temperatura y humedad relativa
            raw_temperature = (data[3] & 0xf) << 16 | data[4] << 8 | data[5]
            raw_humidity = data[1] << 12 | data[2] << 4 | data[3] >> 4
            temperature = (raw_temperature / (2**20 - 1)) * 200 - 50
            humidity = (raw_humidity / (2**20 - 1)) * 100
        except:
            # Manejo de excepciones en caso de error de comunicación
            temperature = "no data"
            humidity = "no data"

        return temperature, humidity
        
    def conectarse(self):
        """
        Intenta establecer conexión con el sensor AHT15.
        """
        try:
            # Enviar comando de inicio de comunicación
            self.i2c.writeto(self.address, bytes([0xE1, 0x08, 0x00]))
            time.sleep_ms(40)
            data = self.i2c.readfrom(self.address, 6)
            # Si la conexión se establece correctamente, se marca como conectado
            self.conectado = True
            print(data)
            print("Conexión establecida")
        except:
            # Si hay algún error en la conexión, se marca como no conectado
            self.conectado = False
            print("Error al establecer conexión")


# Ejemplo de uso:
# i2c = I2C(0, scl=Pin(34), sda=Pin(21),freq=10000)
# sensor = AHT15(i2c)
# 
# while True:
#     
#     time.sleep(2)
#     try:
#         temperature, humidity = sensor.read_sensor()
#         print('Temperatura:', temperature, '°C')
#         print('Humedad:', humidity, '%')
#     except:
#        print("no data")

