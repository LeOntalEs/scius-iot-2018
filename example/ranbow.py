import colorsys
from time import sleep
import library as a
try:
	while True:
		for i in range(0, 360, 5):
			x = list(colorsys.hsv_to_rgb(i/360, 1, 0.2))
			for j in range(len(x)):
				x[j] = int(x[j]*255)
			a.led(*x)
			sleep(0.01)
finally:
	a.reset()