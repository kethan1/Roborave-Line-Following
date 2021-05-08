import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

class Encoder:
    def __init__(self, pin):
        self.pin = GPIO.setup(pin, GPIO.IN)
        self.pin_num = pin
        self.steps = 0
        GPIO.add_event_detect(self.pin_num, GPIO.RISING, callback=lambda call_on_step: self.on_step())

    def on_step(self):
        self.steps += 1
        print(f"Added Step: {self.steps}")
