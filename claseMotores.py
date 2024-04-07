from machine import Pin
import time

class MotorPasoPasoModoSecuencia:
    def __init__(self, pin1=0, pin2=0, pin3=0, pin4=0):
        self.paso1 = Pin(pin1, Pin.OUT)
        self.paso2 = Pin(pin2, Pin.OUT)
        self.paso3 = Pin(pin3, Pin.OUT)
        self.paso4 = Pin(pin4, Pin.OUT)
        self.secuenciaPasos = [
            [1, 0, 0, 1],  # Paso 1: 1001
            [1, 1, 0, 0],  # Paso 2: 1100
            [0, 1, 1, 0],  # Paso 3: 0110
            [0, 0, 1, 1]   # Paso 4: 0011
        ]
        self.secuenciaActual = 0

    def moverDireccionUno(self, delayTiempoMicros):
        i = self.secuenciaActual
        self.paso1.value(self.secuenciaPasos[i][0])
        self.paso2.value(self.secuenciaPasos[i][1])
        self.paso3.value(self.secuenciaPasos[i][2])
        self.paso4.value(self.secuenciaPasos[i][3])
        time.sleep_us(delayTiempoMicros)
        self.secuenciaActual += 1
        if self.secuenciaActual == 4:
            self.secuenciaActual = 0

    def moverDireccionDos(self, delayTiempoMicros):
        i=self.secuenciaActual
        self.paso1.value(self.secuenciaPasos[i][0])
        self.paso2.value(self.secuenciaPasos[i][1])
        self.paso3.value(self.secuenciaPasos[i][2])
        self.paso4.value(self.secuenciaPasos[i][3])
        time.sleep_us(delayTiempoMicros)
        self.secuenciaActual += 1
        if self.secuenciaActual == 4:
            self.secuenciaActual = 0
            
    def moverPasos(self, numPasos, direccion, delayTiempoMicros):
        if direccion:
            for _ in range(numPasos):
                self.moverDireccionUno(delayTiempoMicros)
        else:
            for _ in range(numPasos):
                self.moverDireccionDos(delayTiempoMicros)
            

class MotorPasoPasoModoPulso:
    def __init__(self, pin1=0, pin2=0):
        self.paso1 = Pin(pin1, Pin.OUT)
        self.paso2 = Pin(pin2, Pin.OUT)
        self.conteoPasos=0
        

    def moverDireccionUno(self, delayTiempoMicros):
        self.paso2.value(0)
        self.paso1.value(1)
        time.sleep_us(10)
        self.paso1.value(0)
        time.sleep_us(delayTiempoMicros)

    def moverDireccionDos(self, delayTiempoMicros):
        self.paso2.value(1)
        self.paso1.value(1)
        time.sleep_us(10)
        self.paso1.value(0)
        time.sleep_us(delayTiempoMicros)

    def moverPasos(self, numPasos, direccion, delayTiempoMicros):
        if direccion:
            for _ in range(numPasos):
                self.moverDireccionUno(delayTiempoMicros)
                self.conteoPasos+=numPasos
        else:
            for _ in range(numPasos):
                self.moverDireccionDos(delayTiempoMicros)
                self.conteoPasos-=numPasos
