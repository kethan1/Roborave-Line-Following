import RPi.GPIO as GPIO
import cv2
import scipy.ndimage
import numpy as np
import sys
import time
import picamera
import picamera.array

debug = True
bl_wh = False
if "--prod" in sys.argv[1:]:
    debug = False
elif "--bl_wh" in sys.argv[1:]:
    bl_wh = True

class PID:
    def __init__(self, P, I, D):
        self.P = P
        self.I = I
        self.D = D
        self.iAccumulator = 0
        self.prevError = 0
        self.fileOutput = open("PIDvars.csv")
        self.first = True

    def update(self, target, current):
        error = current-target
        self.iAccumulator += error
        if self.first: 
            self.iAccumulator = 0
            self.prevError = error
            self.first = False
        output = (self.P*error)+(self.iAccumulator*self.I)+((error-self.prevError)*self.D)
        self.prevError = error
        if debug:
            print(f"Equation: {output},I Accumulator: {self.iAccumulator}, P: {self.P*error}, I: {self.I*self.iAccumulator}, D: {self.D*(error-self.prevError)}", file=self.PIDvars)
        return output

    def reset(self):
        self.first = True

def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)

def custom_round(number): 
    return int(round(number))

image = None
currentPID = PID(1, 0, 0)

GPIO.setmode(GPIO.BCM)  

pinlistOut = [17, 26, 13, 6, 5]
pinlistIn = []
lighting_pin = 17
motor1_pin = 26
motor2_pin = 13
motor3_pin = 6
motor4_pin = 5
GPIO.setup(pinlistOut, GPIO.OUT)
# GPIO.output(lighting_pin, 1)
GPIO.output(motor1_pin, 1)
time.sleep(5)
GPIO.output(motor2_pin, 1)
time.sleep(5)
GPIO.output(motor3_pin, 1)
time.sleep(5)
GPIO.output(motor4_pin, 1)
time.sleep(5)

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        while True:
            try:
                image, cropped_image = None, None
                while image is None:
                    camera.capture(stream, 'bgr', use_video_port=True)
                    image = stream.array

                grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, grayscale_image = cv2.threshold(grayscale_image, 100, 255, cv2.THRESH_BINARY_INV)

                height, width = grayscale_image.shape

                if np.sum(grayscale_image) < 50*255:
                    print("Line Lost")
                    sys.exit()

                for current_y in range(0, height, 20):
                    cropped_image = grayscale_image[current_y:current_y+20,0:-1]
                    if np.sum(cropped_image) > 20*255 and current_y+20 < height:
                        center_of_mass_y, center_of_mass_x = scipy.ndimage.center_of_mass(cropped_image)
                        break
                if cropped_image is None:
                    print("Line Lost")
                    sys.exit()

                if not bl_wh:
                    debugging = cv2.circle(image, (custom_round(center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                else:
                    debugging = cv2.circle(grayscale_image, (custom_round(center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                imshow_debug("Video Stream with Circle", debugging)
                
                stream.seek(0)
                stream.truncate()

                if cv2.waitKey(1) & 0xFF == ord('q'): 
                    break
            except KeyboardInterrupt:
                break


cv2.destroyAllWindows()
# GPIO.output(lighting_pin, 0)
GPIO.cleanup()
