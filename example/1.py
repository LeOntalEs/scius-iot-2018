from time import sleep
import library as car

try:
    threshold = 60
    car.onsensor()
    while True:
        car.update()
        humi = int(car.humi())
        if humi > threshold:
            car.led(150, 0, 0)
        else:
            car.led(0, 0, 150)
finally:
    car.reset()
