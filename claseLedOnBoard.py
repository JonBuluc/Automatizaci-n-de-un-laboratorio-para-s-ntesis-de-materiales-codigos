from machine import Pin
import time

class LedOnBoard:
    def __init__(self, pinNum=15):  # Por defecto, el pin es el GPIO15
        self.pin = pinNum
        self.led = Pin(self.pin, Pin.OUT)  # Crear objeto Pin para controlar el LED

    def parpadeo(self, numParpadeos=1, duracionEncendido=100, duracionApagado=100):
        for _ in range(numParpadeos):
            self.led.value(1)  # Encender el pin (nivel alto)
            time.sleep_ms(duracionEncendido)  # Esperar el tiempo de encendido
            self.led.value(0)  # Apagar el pin (nivel bajo)
            time.sleep_ms(duracionApagado)  # Esperar el tiempo de apagado

# Uso de la clase LedOnBoard con el pin GPIO5
led = LedOnBoard(pinNum=15)
led.parpadeo(1)  # Se prenderá y apagará el pin tres veces con los valores por defecto
