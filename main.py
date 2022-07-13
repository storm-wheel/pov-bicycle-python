from sys import stderr
from time import sleep
from PIL import Image
import serial


if __name__ == '__main__':
    image = Image.open('./test.png')
    arduino = serial.Serial()
    arduino.port = '/dev/cu.usbserial-10'
    arduino.baudrate = 57600
    error_waitsec = 3
    image_size = (100, 100)

    image_width, image_height = image.size
    min_length = min(image.size)
    crop_left = (image_width - min_length) / 2
    crop_upper = (image_height - min_length) / 2
    crop_right = (image_width + min_length) / 2
    crop_lower = (image_height + min_length) / 2
    crop_box = (int(crop_left), int(crop_upper),
                int(crop_right), int(crop_lower))
    image_cropped = image.crop(crop_box)
    image_cropped.thumbnail(image_size)
    # image_cropped.show()

    while (arduino.is_open == False):
        try:
            arduino.open()
        except OSError as e:
            print(e.strerror,
                  f'(try again after {error_waitsec} seconds...)', file=stderr)
            sleep(error_waitsec)

    arduino.write(f'{image_width} {image_height}\n'.encode('utf-8'))
    # print(f'{image_width} {image_height}')
    rgb_list = image_cropped.getdata()
    iterator = 0
    for r, g, b in rgb_list:
        print(
            f'\rTransmitting ... \033[90m{100 * iterator / (image_size[0] * image_size[1]):5.2f} %\033[0m', end='', flush=True)
        iterator += 1
        arduino.write(f'{r} {g} {b} '.encode('utf-8'))
        # print(f'{r} {g} {b}', end=' ')
    print('\rTransmitting ... \033[32m[Clear]\033[0m', flush=True)
    arduino.close()
