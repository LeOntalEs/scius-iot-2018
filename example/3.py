from time import sleep
import library as car

try:
    delay = 0.01
    car.offsensor()
    while True:
        car.led(25, 0, 0)
        car.sound('E6', 4)
        sleep(delay)
        car.sound('C6', 4)
        car.led(0, 0, 25)
        sleep(delay)
finally:
    car.reset()