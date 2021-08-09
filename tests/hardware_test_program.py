import inspect
import sys
import os
import json
import time
import cv2
import picamera
import picamera.array
import RPi.GPIO as GPIO
import numpy as np

GPIO.setmode(GPIO.BCM)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

import Libraries.Thunderborg as ThunderBorg
from hall_effect_sensor import Hall_Effect_Sensor
from PID import PID
from CPP_Libraries.Encoder_CPP.encoder import Encoder, init as initialize_encoder


TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
TB.i2cAddress = 10              # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)

# Thunderborg Checks
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print('No ThunderBorg found, check you are attached :)')
    else:
        print(f'No ThunderBorg at address {TB.i2cAddress}, but we did find boards:')
        for board in boards:
            print('    %02X (%d)' % (board, board))
        print('If you need to change the I²C address change the setup line so it is correct, e.g.')
        print('TB.i2cAddress = 0x%02X' % (boards[0]))
    sys.exit()

initialize_encoder()

TB.SetBatteryMonitoringLimits(10, 13)  # Set LED Battery Indicator
print(f'Battery Level Not Underload: {TB.GetBatteryReading()}')

class HardwareFailure(Exception):
    '''
    Will be raised when ever the hardware fails. 
    '''


with open('robot_config.json') as robot_config_file:
    robot_config = json.load(robot_config_file)

P_VALUE: float = robot_config['P']
I_VALUE: float = robot_config['I']
D_VALUE: float = robot_config['D']
MAINTAIN_SPEED_P_VALUE: float = robot_config['MAINTAIN_SPEED_PID']['P']
MAINTAIN_SPEED_I_VALUE: float = robot_config['MAINTAIN_SPEED_PID']['I']
MAINTAIN_SPEED_D_VALUE: float = robot_config['MAINTAIN_SPEED_PID']['D']
GRAYSCALE_THRESHOLD: int = robot_config['GRAYSCALE_THRESHOLD']
BASE_SPEED: float = robot_config['BASE_SPEED']
INTERSECTION_PORTION: float = robot_config['INTERSECTION_PORTION']

encoder_left = Encoder(*robot_config['Encoder_Left'])
encoder_right = Encoder(*robot_config['Encoder_Right'])

def test_motors():
    TB.SetMotor1(1)
    TB.SetMotor2(1)
    time.sleep(0.5)
    for _ in range(10):
        print(f'Battery Level Under Load: {TB.GetBatteryReading()}')
    time.sleep(0.5)
    TB.SetMotor1(0)
    TB.SetMotor2(0)

    if input('Did the motors move forward for 1 second?').lower() == 'no':
        raise HardwareFailure('Motors Did Not Move Forward!')
    else:
        print('Motors moved forward! Test success!')

    TB.SetMotor1(-1)
    TB.SetMotor2(-1)
    time.sleep(1)
    TB.SetMotor1(0)
    TB.SetMotor2(0)

    if input('Did the motors move backward for 1 second?').lower() == 'no':
        raise HardwareFailure('Motors Did Not Move Backward!')
    else:
        print('Motors moved backward! Test success!')

def test_magnet_sensor():
    detected = 0
    def magnet_callback_found(pin: int):
        nonlocal detected
        detected = 1 - hall_effect_sensor.read()

    hall_effect_sensor = Hall_Effect_Sensor(16, magnet_callback_found)

    input('Push Door In. Press enter when you are done: ')
    if detected == 1:
        print('Door has been detected! Test success!')
    else:
        raise HardwareFailure('Magnet Sensor was Not detected!')

    hall_effect_sensor.swap_event_detect()

    input('Push Door Out. Press enter when you are done: ')
    if detected == 0:
        print('Door is not detected any more! Test success!')
    else:
        raise HardwareFailure('Magnet Sensor is still detected!')


def test_camera():
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)
            # Warmup camera
            for _ in range(40):
                camera.capture(stream, 'bgr', use_video_port=True)
                image = stream.array
                 
                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
                )

                cv2.imshow('Image: 0', image)
                cv2.imshow('Grayscale Image: 0', grayscale_image)

                stream.seek(0)
                stream.truncate()

            for image_index in range(2):
                camera.capture(stream, 'bgr', use_video_port=True)
                image = stream.array

                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
                )

                cv2.imshow(f'Image: {image_index  + 1}', image)
                cv2.imshow(f'Grayscale Image: {image_index + 1}', grayscale_image)

                stream.seek(0)
                stream.truncate()

            cv2.waitKey(0)
            cv2.destroyAllWindows()
            if input('Do the images and the grayscale images look good? ').lower() == 'no':
                raise HardwareFailure('Camera images or grayscale thresholding is not working')
            else:
                print('Camera works! Test succeded!')


def test_intersection():
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)
            input('Please put the robot where is can see an intersection. Press enter when done: ')
            for _ in range(40):
                camera.capture(stream, 'bgr', use_video_port=True)
                image = stream.array

                stream.seek(0)
                stream.truncate()

            camera.capture(stream, 'bgr', use_video_port=True)
            image = stream.array

            _, grayscale_image = cv2.threshold(
                cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                GRAYSCALE_THRESHOLD, 255, cv2.THRESH_BINARY_INV
            )

            grayscale_image_resized = cv2.resize(
                grayscale_image, dsize=(
                    int(image.shape[1] * 0.4), int(image.shape[0] * 0.4)
                ),
                interpolation=cv2.INTER_AREA
            )

            pixels_sum = np.sum(grayscale_image_resized, 1)
            max_pixels_pos = np.argmax(pixels_sum)
            max_pixels = pixels_sum[max_pixels_pos] / 255

            intersection_detected = False
            if grayscale_image_resized.shape[1] * INTERSECTION_PORTION <= max_pixels:
                intersection_detected = True

            if not intersection_detected:
                raise HardwareFailure('Intersection detected not working. No intersection detected')
            else:
                print('Intersection detected! Test success!')
            stream.seek(0)
            stream.truncate()


def test_encoder():
    encoder_left = Encoder(*robot_config["Encoder_Left"])
    encoder_right = Encoder(*robot_config["Encoder_Right"])

    input("Hold the robot in the air. It will be moving forward. Press enter when you are ready: ")
    TB.SetMotor1(1)
    TB.SetMotor2(1)

    prevStepsLeft = prevStepsRight = 0
    prevTime = time.time()
    speedsLeft = []
    speedsRight = []

    for _ in range(100):
        cTime = time.time()
        stepsLeft = encoder_left.getSteps()
        stepsRight = encoder_right.getSteps()
        speedLeft = ((stepsLeft - prevStepsLeft) / (cTime - prevTime) * 3) / 3591.84
        speedRight = ((stepsRight - prevStepsRight) / (cTime - prevTime) * 3) / 3591.84 
        prevTime = cTime
        prevStepsLeft = stepsLeft
        prevStepsRight = stepsRight
        # print(f"Left, Steps: {encoder_left.getSteps()}, Direction: {encoder_left.getDirection()}, Speed in rev/sec: {speedLeft}")
        # print(f"Right, Steps: {encoder_right.getSteps()}, Direction: {encoder_right.getDirection()}, Speed in rev/sec: {speedRight}")
        time.sleep(0.01) 

        speedsLeft.append(speedLeft)
        speedsRight.append(speedRight)

    TB.SetMotor1(0)
    TB.SetMotor2(0)    

    if not 1 < sum(speedsLeft[10:]) / len(speedsLeft[10:]) < 1.6:
        raise HardwareFailure('Left encoder is broken for going forward.')
    else:
        print('Test Success! The left encoder works for going forward!')

    if not 1 < sum(speedsRight[10:]) / len(speedsRight[10:]) < 1.6:
        raise HardwareFailure('Right encoder is broken for going forward.')
    else:
        print('Test Success! The right encoder works for going forward!')


    input("Hold the robot in the air. It will be moving backward. Press enter when you are ready: ")
    TB.SetMotor1(-1)
    TB.SetMotor2(-1)

    prevStepsLeft = prevStepsRight = 0
    prevTime = time.time()
    speedsLeft = []
    speedsRight = []

    for _ in range(100):
        cTime = time.time()
        stepsLeft = encoder_left.getSteps()
        stepsRight = encoder_right.getSteps()
        speedLeft = ((stepsLeft - prevStepsLeft) / (cTime - prevTime) * 3) / 3591.84
        speedRight = ((stepsRight - prevStepsRight) / (cTime - prevTime) * 3) / 3591.84 
        prevTime = cTime
        prevStepsLeft = stepsLeft
        prevStepsRight = stepsRight
        # print(f"Left, Steps: {encoder_left.getSteps()}, Direction: {encoder_left.getDirection()}, Speed in rev/sec: {speedLeft}")
        # print(f"Right, Steps: {encoder_right.getSteps()}, Direction: {encoder_right.getDirection()}, Speed in rev/sec: {speedRight}")
        time.sleep(0.01) 

        speedsLeft.append(speedLeft)
        speedsRight.append(speedRight)

    TB.SetMotor1(0)
    TB.SetMotor2(0)    

    if not -1.6 < sum(speedsLeft[10:]) / len(speedsLeft[10:]) < -1:
        raise HardwareFailure('Left encoder is broken for going backward.')
    else:
        print('Test Success! The left encoder works for going backward!')

    if not -1.6 < sum(speedsRight[10:]) / len(speedsRight[10:]) < -1:
        raise HardwareFailure('Right encoder is broken for going backward.')
    else:
        print('Test Success! The right encoder works for going backward!')

if not sys.argv[1:]:
    test_motors()
    test_magnet_sensor()
    test_camera()
    test_intersection()
    test_encoder()
else:
    if '--motors' in sys.argv[1]:
        test_motors()
    if '--magnet' in sys.argv[1:]:
        test_magnet_sensor()
    if '--camera' in sys.argv[1:]:
        test_camera()
    if '--intersection' in sys.argv[1:]:
        test_intersection()
    if '--encoder' in sys.argv[1:]:
        test_encoder()