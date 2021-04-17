import cv2
import scipy.ndimage
import numpy
import sys

debug = True

def imshow_ripoff(image_to_show, title):
    if debug:
        cv2.imshow(image_to_show, title)

imagevar = "images/nothing.jpg"

v1 = cv2.VideoCapture(0)
image = None

while True:
    image = None
    while image is None:
        success, image = v1.read()

    # test_image1 = cv2.imread(imagevar, cv2.IMREAD_GRAYSCALE)
    # test_image_color = cv2.imread(imagevar, cv2.IMREAD_COLOR)

    test_image1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    test_image_color = image
    _, test_image1 = cv2.threshold(test_image1, 115, 255, cv2.THRESH_BINARY_INV)


    height, width = test_image1.shape

    if numpy.sum(test_image1) < 50*255:
        print("lost line")
        sys.exit()

    img1 = None

    for i in range(0, height, 20):
        img1 = test_image1[i:i+20,0:-1]
        if numpy.sum(img1) > 20*255:
            if i+20 < height:
                print(numpy.sum(img1))
                center_of_mass = scipy.ndimage.center_of_mass(img1)
                print(center_of_mass)
                break
    if img1 is None:
        print("line lost")
        sys.exit()

    debugging = cv2.circle(test_image_color, (int(round(center_of_mass[1])), i+int(round(center_of_mass[0]))), 5, (0,0, 255), 1)
    imshow_ripoff("test", debugging)
    key = cv2.waitKey(1)
    
    if key == ord("q"):
        break


# bottom_20_rows = test_image1[0:20,0:-1]
# bottom_20_rows2 = test_image_color[0:20,0:-1]


# center_of_mass = scipy.ndimage.center_of_mass(bottom_20_rows)

# debugging = cv2.circle(bottom_20_rows2, (int(round(center_of_mass[1])), 0), 5, (0,0, 255), 1)

# imshow_ripoff("test", debugging)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

v1.release()
