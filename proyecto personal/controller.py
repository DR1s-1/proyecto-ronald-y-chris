
import pyfirmata

comport = 'COM3'
board = pyfirmata.Arduino(comport)

# Pines de salida
buzzer_pin = board.get_pin('d:7:o')
led_1 = board.get_pin('d:8:o')
led_2 = board.get_pin('d:9:o')
led_3 = board.get_pin('d:10:o')
led_4 = board.get_pin('d:11:o')
led_5 = board.get_pin('d:12:o')

# Configurar como salida (opcional con get_pin, pero más seguro)
for pin in [buzzer_pin, led_1, led_2, led_3, led_4, led_5]:
    pin.mode = 1


def buzzer_on():
    buzzer_pin.write(1)


def buzzer_off():
    buzzer_pin.write(0)


def led(fingerUp):
    # Solo dedo índice levantado
    if fingerUp == [1, 0, 0, 0, 1]:
        buzzer_on()
        led_1.write(1)
        led_2.write(0)
        led_3.write(0)
        led_4.write(0)
        led_5.write(0)
    else:
        buzzer_off()
        led_1.write(1 if fingerUp[1] else 0)
        led_2.write(1 if fingerUp[2] else 0)
        led_3.write(1 if fingerUp[3] else 0)
        led_4.write(1 if fingerUp[4] else 0)
        led_5.write(1 if fingerUp[0] else 0)
