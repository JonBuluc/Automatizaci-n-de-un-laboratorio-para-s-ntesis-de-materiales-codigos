#Prueba del funcionamiento de motores

from machine import ADC
from ClaseMotores import MotorPasoPasoModoSecuencia

# Definición de los pines
pin1 = 14
pin2 = 27
pin3 = 26
pin4 = 25

# Tiempo de espera entre pasos (en microsegundos)
delayTiempoMicros = 2000

# Crear instancia del motor
motor = MotorPasoPasoModoSecuencia(pin1=pin1, pin2=pin2, pin3=pin3, pin4=pin4, modo=True)

# Configuración del ADC
pinADC = 35  # Pin de entrada analógica
adc = ADC(0) # seleccionamos el ADC0, correspondiente al pin 35
adc.atten(ADC.ATTN_11DB)  # Configura la atenuación a 11 dB para un rango de 0-3.3V

while True:
    # Lectura del valor del ADC
    valorADC = adc.read()

    # Movimiento del motor en función del valor del ADC
    if valorADC > 2048:
        motor.moverPasos(numPasos=100, direccion=True, delayTiempoMicros=delayTiempoMicros)
    else:
        motor.moverPasos(numPasos=100, direccion=False, delayTiempoMicros=delayTiempoMicros)
