from ppadb.client import Client
from PIL import Image
import numpy
import time


def check_colour(img, y, x, colour):
    px = list(img[y][x])
    rgb = px[:3]
    res = False

    if rgb == colour:
        res = True

    return res


adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

device.shell('input touchscreen swipe 940 2225 940 2225 1')
device.shell('input touchscreen swipe 800 1800 800 1800 1')
device.shell('input touchscreen swipe 800 1800 800 1800 1')
time.sleep(0.6)

image = device.screencap()
with open('screen.png', 'wb') as f:
    f.write(image)

image = Image.open('screen.png')
image = numpy.array(image, dtype=numpy.uint8)


fav = check_colour(image, 1610, 90, [255, 207, 116])
print(fav)

one_star = check_colour(image, 1610, 95, [255, 204, 114])
two_star = check_colour(image, 1585, 160, [255, 206, 116])
three_star = check_colour(image, 1565, 230, [255, 197, 107])

stars = one_star + two_star + three_star
print(stars)

device.shell('input touchscreen swipe 800 1800 800 1800 1')
