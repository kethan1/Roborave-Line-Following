import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Hall_Effect_Sensor:
    def __init__(self, pin: int, callback=None, bouncetime: int = 25):
        self.pin = GPIO.setup(pin, GPIO.IN)
        self.pin_num = pin
        if callback is None:
            callback = self.detect
        self.bouncetime = bouncetime
        GPIO.add_event_detect(
            self.pin_num, GPIO.FALLING, callback=callback, bouncetime=bouncetime
        )
        self.callback = callback

    def detect(self, pin: int):
        print(f"Magnet Detected on Pin {pin}")

    def swap_event_detect(self):
        GPIO.remove_event_detect(self.pin_num)
        if self.callback is not None:
            GPIO.add_event_detect(
                self.pin_num,
                GPIO.RISING,
                callback=self.callback,
                bouncetime=self.bouncetime,
            )

    def read(self):
        return GPIO.input(self.pin_num)

    def __del__(self):
        GPIO.remove_event_detect(self.pin_num)
