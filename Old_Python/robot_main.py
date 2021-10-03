#!/usr/bin/env python3

import sys
import time
import json
import timeit

import cv2
import numpy as np
import picamera
import picamera.array
import RPi.GPIO as GPIO
import scipy.ndimage

from PID import PID

with open("robot_config.json") as robot_config_file:
    robot_config = json.load(robot_config_file)

debug = bool(robot_config["debug"])
bl_wh = False
P_VALUE = robot_config["P"]
I_VALUE = robot_config["I"]
D_VALUE = robot_config["D"]
GRAYSCALE_THRESHOLD = robot_config["GRAYSCALE_THRESHOLD"]
if "--prod" in sys.argv[1:]:
    debug = False
if "--bl_wh" in sys.argv[1:]:
    bl_wh = True
if "--P" in sys.argv[1:]:
    P_VALUE = float(sys.argv[sys.argv.index("--P") + 1])
if "--I" in sys.argv[1:]:
    I_VALUE = float(sys.argv[sys.argv.index("--I") + 1])
if "--D" in sys.argv[1:]:
    D_VALUE = float(sys.argv[sys.argv.index("--D") + 1])


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


def custom_round(number):
    return int(round(number))


image = None
currentPID = PID(P=P_VALUE, I=I_VALUE, D=D_VALUE, debug=debug)

GPIO.setmode(GPIO.BCM)

pinlistOut = [26, 13, 6, 5, 12, 16]
pinlistIn = []
# IN1 - left forward
# IN2 - left backward
# IN3 - right forward
# IN4 - right backward
# ENA - left speed
# ENB - right speed
IN1 = robot_config["IN1"]
IN2 = robot_config["IN2"]
IN3 = robot_config["IN3"]
IN4 = robot_config["IN4"]
ENA = robot_config["ENA"]
ENB = robot_config["ENB"]
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.output(pinlistOut, 0)
ENA_PWM = GPIO.PWM(ENA, 200)
ENB_PWM = GPIO.PWM(ENB, 200)
BASE_SPEED = robot_config["BASE_SPEED"]
LEFT = 0
RIGHT = 1
FORWARD = 0
BACKWARD = 1

ENA_PWM.start(1)
ENB_PWM.start(1)


def motor_move(side, direction, speed):
    print(f"Side: {side}, Direction: {direction}, Speed: {speed}")
    if side == LEFT:
        if direction == FORWARD:
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN1, GPIO.HIGH)
            ENA_PWM.ChangeDutyCycle(speed)
        elif direction == BACKWARD:
            print("pin", IN2)
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
            ENA_PWM.ChangeDutyCycle(speed)
    elif side == RIGHT:
        if direction == FORWARD:
            GPIO.output(IN4, GPIO.LOW)
            GPIO.output(IN3, GPIO.HIGH)
            ENB_PWM.ChangeDutyCycle(speed)
        elif direction == BACKWARD:
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.HIGH)
            ENB_PWM.ChangeDutyCycle(speed)


# def reset_all_motors():
#     ENA_PWM.stop()
#     ENB_PWM.stop()
#     GPIO.output([26, 13, 6, 5], GPIO.LOW)


def motor_move_interface(equation_output):
    motor_left = BASE_SPEED
    motor_right = BASE_SPEED

    # positive - left faster
    # negative - right faster

    motor_left -= equation_output
    motor_right += equation_output

    print(equation_output)

    if motor_left > robot_config["MAX_SPEED"]:
        motor_left = robot_config["MAX_SPEED"]
    elif motor_left < -robot_config["MAX_SPEED"]:
        motor_left = -robot_config["MAX_SPEED"]

    if motor_right > robot_config["MAX_SPEED"]:
        motor_right = robot_config["MAX_SPEED"]
    elif motor_right < -robot_config["MAX_SPEED"]:
        motor_right = -robot_config["MAX_SPEED"]

    print(f"Motor Speeds, Left: {motor_left}, Right: {motor_right}")

    if motor_left > 0:
        print("Left, Forward")
        motor_move(LEFT, FORWARD, abs(motor_left))
    elif motor_left < 0:
        print("Left, Backward")
        motor_move(LEFT, BACKWARD, abs(motor_left))

    if motor_right > 0:
        print("Right, Forward")
        motor_move(RIGHT, FORWARD, abs(motor_right))
    elif motor_right < 0:
        print("Right, Backward")
        motor_move(RIGHT, BACKWARD, abs(motor_right))


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        while True:
            try:
                start_time = timeit.default_timer()
                image, cropped_image = None, None
                while image is None:
                    camera.capture(stream, "bgr", use_video_port=True)
                    image = stream.array
                image = cv2.rotate(image, cv2.cv2.ROTATE_180)
                # grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD,
                    255,
                    cv2.THRESH_BINARY_INV,
                )

                height, width = grayscale_image.shape

                if np.sum(grayscale_image) < 50 * 255:
                    print("Line Lost")
                    GPIO.cleanup()
                    currentPID.close()
                    print(2)
                    sys.exit()

                for current_y in range(0, height, 20):
                    cropped_image = grayscale_image[current_y : current_y + 20, 0:-1]
                    if np.sum(cropped_image) > 20 * 255 and current_y + 20 < height:
                        (
                            center_of_mass_y,
                            center_of_mass_x,
                        ) = scipy.ndimage.center_of_mass(cropped_image)
                        break
                if cropped_image is None:
                    print("Line Lost")
                    GPIO.cleanup()
                    currentPID.close()
                    print(1)
                    sys.exit()

                pid_equation_output = currentPID.update(width / 2, center_of_mass_x)

                print(pid_equation_output)
                motor_move_interface(pid_equation_output)

                if not bl_wh:
                    debugging = cv2.circle(
                        image,
                        (
                            custom_round(center_of_mass_x),
                            current_y + custom_round(center_of_mass_y),
                        ),
                        10,
                        (0, 0, 255),
                        10,
                    )
                else:
                    grayBGR = cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR)
                    debugging = cv2.circle(
                        grayBGR,
                        (
                            custom_round(center_of_mass_x),
                            current_y + custom_round(center_of_mass_y),
                        ),
                        10,
                        (0, 0, 255),
                        10,
                    )
                debugging = cv2.rotate(debugging, cv2.cv2.ROTATE_180)
                imshow_debug("Video Stream with Circle", debugging)

                stream.seek(0)
                stream.truncate()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                end_time = timeit.default_timer()
                print(f"Frame Time: {(end_time-start_time)}")
            except KeyboardInterrupt:
                break


print("Ending Program")
cv2.destroyAllWindows()
GPIO.cleanup()
currentPID.close()
