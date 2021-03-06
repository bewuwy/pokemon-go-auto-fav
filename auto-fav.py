from ppadb.client import Client
from PIL import Image
from os import remove
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

    if debug:
        print(f'{rgb} {colour_name}')

    if colour_name in colours:
        res = True

    return res


adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()

if len(devices) == 0:
    print('no device attached')
    quit()

device = devices[0]

device.shell('input touchscreen swipe 940 2225 940 2225 10')
device.shell('input touchscreen swipe 800 1800 800 1800 10')
device.shell('input touchscreen swipe 800 1800 800 1800 10')

n = input("Pokemon number: ")
debug = False

while not n.isnumeric():
    if n.lower() == "debug" or debug:
        n = input("Pokemon number (Debug Mode): ")
        debug = True
    else:
        n = input("Pokemon number: ")
n = int(n)

print("------------------")
crit = 0
faved = 0
perfect = 0
start_time = time.time()

for i in range(n):
    print(f'{i + 1}/{n}')
    time.sleep(0.5)

    t = time.time()
    image = device.screencap()
    with open('screen.png', 'wb') as f:
        f.write(image)
    image = Image.open('screen.png')
    image = numpy.array(image, dtype=numpy.uint8)

    if debug:
        print(f'Time to save and load screenshot: {round(time.time() - t, 3)} s')

    yel_colours = ['khaki', 'sandybrown', 'gold', 'navajowhite']
    red_colours = ['red', 'pink', 'lightcoral']

    t = time.time()
    fav = check_colour(image, 270, 975, yel_colours)

    one_star = check_colour(image, 1610, 95, yel_colours)
    two_star = check_colour(image, 1585, 160, yel_colours)
    three_star = check_colour(image, 1565, 230, yel_colours)

    stars = int(one_star + two_star + three_star)
    print(f'{fav} {stars}')

    full_atk = check_colour(image, 1810, 475, red_colours)
    full_def = check_colour(image, 1910, 475, red_colours)
    full_hp = check_colour(image, 2010, 475, red_colours)

    if debug:
        print(f'Time to check colours: {round(time.time() - t, 3)} s')

    if full_atk and full_def and full_hp:
        print("WOW! This Pokemon has perfect IV!")
        perfect += 1

    if stars > 1 and not fav:
        t = time.time()
        print("Adding fav")
        device.shell('input touchscreen swipe 970 270 970 270 10')
        crit += 1
        faved += 1

        if debug:
            print(f'Time to add favourite: {round(time.time() - t, 3)} s')
    elif stars > 1:
        print("Already fav")
        crit += 1
    else:
        print("Shouldn't be fav")

    t = time.time()
    device.shell('input touchscreen swipe 800 1800 400 1800 100')

    if debug:
        print(f'Time to swipe to another pokemon: {round(time.time() - t, 3)} s')

    print("------------------")

device.shell('input touchscreen swipe 800 1800 400 1800 10')

elapsed_time = time.time() - start_time
print(f'Analyzed {n} Pokemon/s in {time.strftime("%M:%S", time.gmtime(elapsed_time))}')
print(f'About {round(int(elapsed_time) / n, 2)} seconds for one Pokemon')
print(f'Found {crit} pokemon matching criteria and added fav to {faved} of them!')
if perfect > 0:
    print(f'Nice! You have {perfect} perfect IV Pokemon!')
print(f'So about {round(crit / n, 3) * 100}% of your Pokemon are good')
print("------------------")
print(f'{round(1 / (int(elapsed_time) / n), 2)} Pokemon/s')
print(f'{round(1 / (int(elapsed_time) / n) * 60, 2)} Pokemon/min')
print(f'{round(1 / (int(elapsed_time) / n) * 60 * 60, 2)} Pokemon/h')

remove("screen.png")

# Time distribution:
# 3.0s when not adding fav
# 3.6s when adding fav
#
# (0.6s - adding fav)
# 1.5s - taking screenshot
# 0.9s - swiping between
# 0.5s - waiting for animation to end
# 0.009s - checking colours
