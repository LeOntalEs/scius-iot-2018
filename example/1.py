from time import sleep
import library as car

import keyboard

try:
    car.offsensor()
    while True:
        if keyboard.is_pressed('w'):
            car.motor(999,999)
        elif keyboard.is_pressed('s'):
            car.motor(-999,-999)
        elif keyboard.is_pressed('a'):
            car.motor(-999,999)
        elif keyboard.is_pressed('d'):
            car.motor(999,-999)
        else:
            car.motor(0,0)
        sleep(0.2)
finally:
    car.reset()
