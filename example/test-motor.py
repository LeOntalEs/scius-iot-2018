from time import sleep
import library as car

try:
    while True:
        car.motor(999, 999)
        sleep(1)
        car.stop()
        sleep(1)

        car.motor(-999, -999)
        sleep(1)
        car.stop()
        sleep(1)

        # car.motor(0, -999)
        # sleep(1)
        # car.stop()
        # sleep(0.2)

        # car.motor(999, 0)
        # sleep(1)
        # car.stop()
        # sleep(0.2)
finally:
    car.reset()
