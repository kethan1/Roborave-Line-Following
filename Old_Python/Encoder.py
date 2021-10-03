import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Encoder:
    def __init__(self, pin):
        self.pin = GPIO.setup(pin, GPIO.IN)
        self.pin_num = pin
        self.steps = 0
        GPIO.add_event_detect(self.pin_num, GPIO.RISING, callback=self.on_step)

    def on_step(self, pin):
        self.steps += 1
        print(f"Added Step: {self.steps}, Pin Number: {self.pin_num}")

    def rotations(self):
        return self.steps / 3591.84


class Encoder_quadrature:
    def __init__(self, pinA, pinB):
        self.pinA = pinA
        self.pinB = pinB
        GPIO.setup(self.pinA, GPIO.IN)
        GPIO.setup(self.pinB, GPIO.IN)
        self.steps = 0
        GPIO.add_event_detect(self.pinA, GPIO.RISING, callback=self.on_step)

    def on_step(self, pinA):
        if GPIO.input(self.pinB) == GPIO.LOW:
            self.steps -= 1
            print(
                f"Subtracted Step: {self.steps}, Pin Number: {self.pinA}, {self.pinB}"
            )
        else:
            self.steps += 1
            print(f"Added Step: {self.steps}, Pin Number: {self.pinA}, {self.pinB}")

    def rotations(self):
        return self.steps / 3591.84
