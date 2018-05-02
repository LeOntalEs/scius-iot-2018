import library as toy
from time import sleep # sleep(second)
while True:
	# pass
# toy.onsensor()
# for i in xrange(1,255):
# 	toy.led(i,0,0)
# toy.led(0,i,0)
# toy.led(0,0,i)

	delay = 0
	step = 5
	for c in range(3):
		intensity = [0, 0, 0]
		for i in range(0, 255, step):
			intensity[c] = i
			toy.led(*intensity)
			sleep(delay)
		for i in range(255, 0, -step):
			intensity[c] = i
			toy.led(*intensity)
			sleep(delay)
			
	# sleep(1)
# toy.temp()
# toy.humi()