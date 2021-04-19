import cv2
import scipy.ndimage
import numpy as np
import sys
import picamera
import picamera.array

debug = True


def imshow_debug(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)


def custom_round(number):
    return int(round(number))


current_camera = cv2.VideoCapture(0)
image = None


with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)
        while True:
            try:
                image, cropped_image = None, None
                while image is None:
                    camera.capture(stream, 'bgr', use_video_port=True)
                    image = stream.array
                    # _, image = current_camera.read()

                grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, grayscale_image = cv2.threshold(
                    grayscale_image, 115, 255, cv2.THRESH_BINARY_INV)

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

                debugging = cv2.circle(image, (custom_round(
                    center_of_mass_x), current_y+custom_round(center_of_mass_y)), 10, (0, 0, 255), 10)
                imshow_debug("Video Stream with Circle", debugging)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                stream.seek(0)
                stream.truncate()
            except KeyboardInterrupt:
                break


cv2.destroyAllWindows()
current_camera.release()
