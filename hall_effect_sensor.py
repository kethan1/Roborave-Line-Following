import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Hall_Effect_Sensor:
    def __init__(self, pin: int, callback=None, bouncetime: int=200):
        self.pin = GPIO.setup(pin, GPIO.IN)
        self.pin_num = pin
        if callback is None:
            callback = self.detect
        GPIO.add_event_detect(self.pin_num, GPIO.FALLING, callback=self.detect, bouncetime=bouncetime)

    def detect(self, pin: int):
        print(f"Magnet Detected on Pin {pin}")

    def __del__(self):
        GPIO.remove_event_detect(self.pin_num)
