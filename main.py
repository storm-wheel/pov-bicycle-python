from sys import stderr
from time import sleep
from PIL import Image
from math import sin, cos, pi
import serial


def get_polar_coordinate_image(image: Image, pixel_per_line: int, pices: int) -> Image:
    """
    Get polar coordinate image.
    :param image: Image to get polar coordinate image from.
    :return: Polar coordinate image.
    """
    degree_step = 360 / pices
    polar_coordinate_image = Image.new(
        "RGB", (pices, pixel_per_line))
    square_image, image_size = get_square_image_and_size(image)
    start_coord = (image_size // 2, image_size // 2)
    radius = image_size // 2
    for i in range(pices):
        theta = i * degree_step
        end_x = start_coord[0] + int(radius * cos(theta * pi / 180))
        end_y = start_coord[1] + int(radius * sin(theta * pi / 180))
        end_coord = (end_x, end_y)
        line = get_line_of_image(
            square_image, start_coord, end_coord, pixel_per_line)
        for r in range(pixel_per_line):
            polar_coordinate_image.putpixel((i, r), line[r])
    return polar_coordinate_image


def get_square_image_and_size(image: Image) -> Image:
    """
    Get square image.
    :param image: Image to get square image from.
    :return: Square image.
    """
    center_coord = (image.width // 2, image.height // 2)
    image_size = min(image.width, image.height)
    square_image = Image.new("RGB", (image_size, image_size))
    for y in range(image_size):
        for x in range(image_size):
            origin_x = center_coord[0] - image_size // 2 + x
            origin_y = center_coord[1] - image_size // 2 + y
            origin_pixel = image.getpixel((origin_x, origin_y))
            square_image.putpixel((x, y), origin_pixel)
    return square_image, image_size


def get_line_of_image(image: Image, start_coord: tuple, end_coord: tuple, step: int) -> list:
    """
    Get a line of pixels from an image.
    :param image: Image to get line from.
    :param start_coord: Start coordinate of line.
    :param end_coord: End coordinate of line.
    :param step: step of line.
    :return: Line of pixels.
    """
    x_diff = end_coord[0] - start_coord[0]
    y_diff = end_coord[1] - start_coord[1]
    x_step = x_diff / step
    y_step = y_diff / step
    x = start_coord[0]
    y = start_coord[1]
    line = []
    for _ in range(step):
        line.append(image.getpixel((int(x), int(y))))
        x += x_step
        y += y_step
    return line


if __name__ == '__main__':
    image = Image.open('./test.png')
    # image = Image.open('./heroes-of-the-storm-logo.png')
    arduino = serial.Serial()
    arduino.port = '/dev/cu.usbserial-10'
    arduino.baudrate = 57600
    error_waitsec = 3
    r_size = 100

    square_image, _ = get_square_image_and_size(image)
    polar_image = get_polar_coordinate_image(image, r_size, 30)
    # square_image.show()
    # polar_image.show()

    while (arduino.is_open == False):
        try:
            arduino.open()
        except OSError as e:
            print(e.strerror,
                  f'(try again after {error_waitsec} seconds...)', file=stderr)
            sleep(error_waitsec)

    arduino.write(f'{r_size} {r_size}\n'.encode('utf-8'))
    print(f'Size of image in transit: {r_size}x{r_size}')
    rgb_list = polar_image.getdata()
    iterator = 0
    for r, g, b in rgb_list:
        print(
            f'\rTransmitting ... \033[90m{100 * iterator / (r_size ** 2):5.2f} %\033[0m', end='', flush=True)
        iterator += 1
        arduino.write(f'{r} {g} {b} '.encode('utf-8'))
    print('\rTransmitting ... \033[32m[Clear]\033[0m', flush=True)
    arduino.close()
