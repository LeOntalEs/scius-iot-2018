import supportMain2 as car
from time import sleep # sleep(secound)

while True:
	# for i in range(0,16):
	# 	car.led(255-i*16,i*16,0)
	# 	sleep(0.1)
	# for i in range(0,16):
	# 	car.led(0,255-i*16,i*16)
	# 	sleep(0.1)
	# for i in range(0,16):
	# 	car.led(i*16,0,255-i*16)
	# 	sleep(0.1)
	car.motor(999,999)
	sleep(1)
	car.motor(0,0)
	sleep(1)
	car.motor(-999,-999)
	sleep(1)
	car.motor(0,0)
	sleep(1)

