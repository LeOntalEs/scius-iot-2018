from time import sleep
import library as car

STEP = 10
DELAY = 0.01


def myabs(x):
    if x < 0:
        return -x
    else:
        return x
        
try:
    while True:
        # 
        # RED INTENSITY
        # 
        for intensity in range(0, 150, STEP):
            car.led(intensity, 0, 0)
            sleep(DELAY)
        for intensity in range(0, 150, STEP):
            car.led(150-intensity, 0, 0)
            sleep(DELAY)

        # 
        # GREEN INTENSITY with 
        # 
        for intensity in range(0, 150, STEP):
            car.led(0, intensity, 0)
            sleep(DELAY)
        for intensity in range(150, 0, -STEP):
            car.led(0, intensity, 0)
            sleep(DELAY)

        # 
        # BLUE INTENSITY with single loop
        #
        for intensity in range(0, 150*2, STEP):
            car.led(0, 0, 150-myabs(150-intensity))
            sleep(DELAY)

finally:
    car.reset()
