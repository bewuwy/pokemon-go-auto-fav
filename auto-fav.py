from ppadb.client import Client
from PIL import Image
import numpy
import time
import webcolors


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name


def check_colour(img, y, x, colours):
    px = list(img[y][x])
    rgb = tuple(px[:3])
    res = False
    colour_name = closest_colour(rgb)

    # print(rgb)
    # print(colour_name)

    if colour_name in colours:
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

n = int(input("Pokemon number: "))
start_time = time.time()
for i in range(n):
    time.sleep(0.8)

    image = device.screencap()
    with open('screen.png', 'wb') as f:
        f.write(image)

    image = Image.open('screen.png')
    image = numpy.array(image, dtype=numpy.uint8)

    yel_colours = ['khaki', 'sandybrown', 'gold', 'navajowhite']

    fav = check_colour(image, 270, 975, yel_colours)
    print(fav)

    one_star = check_colour(image, 1610, 95, yel_colours)
    two_star = check_colour(image, 1585, 160, yel_colours)
    three_star = check_colour(image, 1565, 230, yel_colours)

    stars = int(one_star + two_star + three_star)
    print(stars)

    if stars > 1 and not fav:
        print("Adding fav")
        device.shell('input touchscreen swipe 970 270 970 270 1')
    elif stars > 1:
        print("Already fav")
    else:
        print("Shouldn't be fav")

    device.shell('input touchscreen swipe 800 1800 400 1800 100')

    print("------------------")

device.shell('input touchscreen swipe 800 1800 400 1800 1')

elapsed_time = time.time() - start_time
print(f'Analyzed {n} Pokemons in {time.strftime("%M:%S", time.gmtime(elapsed_time))}')
