import cv2
import scipy.ndimage
import numpy as np
import RPi.GPIO as GPIO
import picamera
import picamera.array
import sys
import time
import csv

debug = True
bl_wh = False
P_VALUE = 1
if "--prod" in sys.argv[1:]:
    debug = False
if "--bl_wh" in sys.argv[1:]:
    bl_wh = True
if "--P" in sys.argv[1:]:
    P_VALUE = sys.argv[sys.argv.index("--P")+1]


class PID:
    def __init__(self, P, I, D):
        self.P = P
        self.I = I
        self.D = D
        self.iAccumulator = 0
        self.prevError = 0
        self.fileOutput = open("PIDvars.csv", "w")
        self.writePointer = csv.writer(
            self.fileOutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        self.first = True

    def update(self, target, current):
        error = current-target
        self.iAccumulator += error
        if self.first:
            self.iAccumulator = 0
            self.prevError = error
            self.first = False
        output = (self.P*error)+(self.iAccumulator*self.I) + \
            ((error-self.prevError)*self.D)
        if debug:
            self.writePointer.writerow([
                f"Equation: {output}",
                f"I Accumulator: {self.iAccumulator}",
                f"Error: {error}",
                f"Prev Error: {self.prevError}",
                f"P: {self.P*error}",
                f"I: {self.I*self.iAccumulator}",
                f"D: {self.D*(error-self.prevError)}"
            ])
        self.prevError = error

        return output

    def reset(self):
        self.first = True

    def close(self):
        self.fileOutput.close()


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


def custom_round(number):
    return int(round(number))


image = None
currentPID = PID(P=P_VALUE, I=0, D=0)

GPIO.setmode(GPIO.BCM)

pinlistOut = [17, 26, 13, 6, 5, 12, 16]
pinlistIn = []
lighting_pin = 17
# 13 (IN1) - left forward
# 6 (IN2) - left backward
# 26 (IN3) - right backward
# 5 (IN4) - right forward
IN1 = 13
IN2 = 6
IN3 = 26
IN4 = 5
ENA = 16
ENB = 12
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.output(pinlistOut, 0)
# GPIO.output(lighting_pin, 1)
ENA_PWM = GPIO.PWM(ENA, 2000)
ENB_PWM = GPIO.PWM(ENB, 2000)


def motor_move(side, direction, speed):
    if side == "left":
        if direction == "forward":
            GPIO.output(IN1, 1)
            ENA_PWM.start(speed)
        elif direction == "backward":
            GPIO.output(IN2, 1)
            ENA_PWM.start(speed)
    elif side == "right":
        if direction == "forward":
            GPIO.output(IN3, 1)
            ENB_PWM.start(speed)
        elif direction == "backward":
            GPIO.output(IN4, 1)
            ENB_PWM.start(speed)


def reset_motors():
    ENA_PWM.stop()
    ENB_PWM.stop()
    GPIO.output([26, 13, 6, 5, 16, 12], 0)


def motor_move_interface(equation_output):
    motor_left = 50
    motor_right = 50
    # positive - right faster
    # negative - left faster
    if equation_output > 50:
        equation_output = 50
    elif equation_output < -150:
        equation_output = -150
    motor_left -= equation_output
    motor_right += equation_output
    reset_motors()
    if motor_left > 100:
        motor_left = 100
    if motor_right > 100:
        motor_right = 100
    if motor_left < -100:
        motor_left = -100
    if motor_right < -100:
        motor_right = -100
    if motor_left != 0:
        if motor_left < 0:
            motor_move("left", "backward", abs(motor_left))
        else:
            motor_move("left", "forward", abs(motor_left))
    if motor_right != 0:
        if motor_right < 0:
            motor_move("right", "backward", abs(motor_right))
        else:
            motor_move("right", "forward", abs(motor_right))


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
                _, grayscale_image = cv2.threshold(
                    grayscale_image, 80, 255, cv2.THRESH_BINARY_INV)

                height, width = grayscale_image.shape

                if np.sum(grayscale_image) < 50*255:
                    print("Line Lost")
                    sys.exit()

                for current_y in range(0, height, 20):
                    cropped_image = grayscale_image[current_y:current_y+20, 0:-1]
                    if np.sum(cropped_image) > 20*255 and current_y+20 < height:
                        center_of_mass_y, center_of_mass_x = scipy.ndimage.center_of_mass(
                            cropped_image)
                        break
                if cropped_image is None:
                    print("Line Lost")
                    sys.exit()

                pid_equation_output = currentPID.update(
                    width/2, center_of_mass_x)

                print(pid_equation_output)
                motor_move_interface(pid_equation_output)

                if not bl_wh:
                    debugging = cv2.circle(image, (custom_round(
                        center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                else:
                    debugging = cv2.circle(grayscale_image, (custom_round(
                        center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
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
currentPID.close()
