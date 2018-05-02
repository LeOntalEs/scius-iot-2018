from time import sleep
import library as a

a.offsensor()
try:
	for x in range(4):
		a.motor(999,999)
		sleep(1)
		a.motor(500,0)
		sleep(0.5)
finally:
	a.stop()