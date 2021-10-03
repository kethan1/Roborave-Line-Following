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

expected_behavior = {
    5: "left backward",
    26: "left forward",
    13: "right forward",
    6: "right backward",
}

GPIO.setup(pins + EN_PINs, GPIO.OUT)
GPIO.output(pins, 0)
GPIO.output(EN_PINs, 1)
try:
    for pin in pins:
        print(f"Pin {pin}, Direction: {expected_behavior[pin]} for 5 seconds")
        GPIO.output(pin, 1)
        time.sleep(5)
        GPIO.output(pin, 0)
        time.sleep(1)
        input()
except KeyboardInterrupt:
    pass
GPIO.cleanup()
