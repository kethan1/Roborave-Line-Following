import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pins = [13, 5, 6, 26]
EN_PINs = [16, 12]

# 5 - left backward
# 26 - left forward
# 13 - right forward
# 6 - right backward

GPIO.setup(pins+EN_PINs, GPIO.OUT)
GPIO.output(EN_PINs, 1)
try:
    for pin in pins:
        GPIO.output(pin, 1)
        time.sleep(5)
        GPIO.output(pin, 0)
        time.sleep(1)
except KeyboardInterrupt:
    pass
GPIO.cleanup()
