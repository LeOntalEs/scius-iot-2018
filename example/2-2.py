from time import sleep
import library as car

try:
    step = 10
    delay = 0.1
    while True:
        for c in range(3):
            intensity = [0, 0, 0]
            for i in range(0, 150*2, step):
                intensity[c] = 150-abs(150-i)
                car.led(*intensity)
                sleep(0.05)
finally:
    car.reset()
