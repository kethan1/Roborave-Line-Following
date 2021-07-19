import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Hall_Effect_Sensor:
    def __init__(self, pin, callback=None):
        self.pin = GPIO.setup(pin, GPIO.IN)
        self.pin_num = pin
        if callback is None:
            callback = self.detect
        GPIO.add_event_detect(self.pin_num, GPIO.FALLING, callback=self.detect)

    def detect(self, pin):
        print(f"Magnet Detected on Pin {pin}")
