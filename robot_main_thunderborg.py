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

import Libraries.ThunderBorg3 as ThunderBorg
from PID import PID
import Encoder_CPP.encoder as Encoder

TB = ThunderBorg.ThunderBorg()  # Create a new ThunderBorg object
# TB.i2cAddress = 0x15          # Uncomment and change the value if you have changed the board address
TB.Init()                       # Set the board up (checks the board is connected)

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

TB.SetBatteryMonitoringLimits(9.5, 12)

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
    P_VALUE = float(sys.argv[sys.argv.index("--P")+1])
if "--I" in sys.argv[1:]:
    I_VALUE = float(sys.argv[sys.argv.index("--I")+1])
if "--D" in sys.argv[1:]:
    D_VALUE = float(sys.argv[sys.argv.index("--D")+1])


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)

def custom_round(number):
    return int(round(number))

image = None
currentPID = PID(P=P_VALUE, I=I_VALUE, D=D_VALUE, debug=debug)

GPIO.setmode(GPIO.BCM)

pinlistOut = []
pinlistIn = [25, 22, 24, 23]
# Motor1 - Right
# Motor2 - Left
GPIO.setup(pinlistOut, GPIO.OUT)
GPIO.setup(pinlistIn, GPIO.IN)
GPIO.output(pinlistOut, 0)
BASE_SPEED = robot_config["BASE_SPEED"]
LEFT = 0
RIGHT = 1

# encoder1 = Encoder(25)
# encoder2 = Encoder(22)
# encoder3 = Encoder(24)
# encoder4 = Encoder(23)

def motor_move(side, speed):
    print(f"Side: {side}, Speed: {speed}")
    if side == LEFT:
        TB.SetMotor1(speed)
    elif side == RIGHT:
        TB.SetMotor2(speed)


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

    motor_move(LEFT, motor_left)
    motor_move(RIGHT, motor_right)

    if motor_left > 0:
        print("Left, Forward")
    elif motor_left < 0:
        print("Left, Backward")

    if motor_right > 0:
        print("Right, Forward")
    elif motor_right < 0:
        print("Right, Backward")

print(1)
with picamera.PiCamera() as camera:
    print(2)
    with picamera.array.PiRGBArray(camera) as stream:
        print(3)
        camera.resolution = (320, 240)
        while True:
            try:
                # start_time = timeit.default_timer()
                image, cropped_image = None, None
                while image is None:
                    camera.capture(stream, "bgr", use_video_port=True)
                    image = stream.array
                image = cv2.rotate(image, cv2.cv2.ROTATE_180)
                
                _, grayscale_image = cv2.threshold(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), GRAYSCALE_THRESHOLD, \
                    255, cv2.THRESH_BINARY_INV
                )

                height, width = grayscale_image.shape

                if np.sum(grayscale_image) < 50*255:
                    print("Line Lost")
                    GPIO.cleanup()
                    currentPID.close()
                    break

                for current_y in range(0, height, 20):
                    cropped_image = grayscale_image[current_y:current_y+20, 0:-1]
                    if np.sum(cropped_image) > 20*255 and current_y+20 < height:
                        center_of_mass_y, center_of_mass_x = scipy.ndimage.center_of_mass(
                            cropped_image)
                        break
                if cropped_image is None:
                    print("Line Lost")
                    GPIO.cleanup()
                    currentPID.close()
                    print(1)
                    sys.exit()

                pid_equation_output = currentPID.update(
                    width/2, center_of_mass_x)

                print(pid_equation_output)
                motor_move_interface(pid_equation_output)

                if not bl_wh:
                    debugging = cv2.circle(image, (custom_round(
                        center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                else:
                    grayBGR = cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR)
                    debugging = cv2.circle(grayBGR, (custom_round(
                        center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                debugging = cv2.rotate(debugging, cv2.cv2.ROTATE_180)
                imshow_debug("Video Stream with Circle", debugging)
    
                stream.seek(0)
                stream.truncate()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
                # end_time = timeit.default_timer()
                # print(f"Frame Time: {(end_time-start_time)}")
            except KeyboardInterrupt:
                break
        


print("Ending Program")
cv2.destroyAllWindows()
GPIO.cleanup()
TB.MotorsOff()
currentPID.close()