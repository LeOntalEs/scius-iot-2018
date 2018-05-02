import library as car
from time import sleep # sleep(second)

car.offsensor()
# car.update()
# car.temp()
# car.humi()
for i in range(255):
	car.led(i,0,0)
