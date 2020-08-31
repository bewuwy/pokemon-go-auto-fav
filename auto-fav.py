from ppadb.client import Client
from PIL import Image
import numpy
import time

adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

image = device.screencap()
with open('screen.png', 'wb') as f:
    f.write(image)

image = Image.open('screen.png')
image = numpy.array(image, dtype=numpy.uint8)

pixel = list(image[270][975])
rgb = pixel[:3]

print(rgb)
if rgb == [245, 192, 13]:
    print("fav")
else:
    print("not fav")
