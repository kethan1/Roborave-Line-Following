import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
motor_pins = [5,6,13,26]
en_pins = [12,16]
GPIO.setup(motor_pins+en_pins, GPIO.OUT)
GPIO.output(motor_pins+en_pins, GPIO.LOW)
GPIO.cleanup()
