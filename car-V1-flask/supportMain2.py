import http.client
import json
import math
from time import sleep # sleep(secound)

# locationHostIP = "localhost:5000"
locationHostIP = "192.168.1.3:5000"
def request(path):
	connection = http.client.HTTPConnection(locationHostIP)
	connection.request("GET",path)
	response = connection.getresponse()
	data = response.read().decode("utf-8") 
	connection.close()
	return data

def waitDone():
	ans = ""
	while ans != "OK":
		ans = request('do/standby')

def led(r,g,b):
	if r > 255:
		r = 255
	elif r < 0:
		r = 0
	if g > 255:
		g = 255
	elif g < 0:
		g = 0
	if b > 255:
		b = 255
	elif b < 0:
		b = 0
	
	request('do/led?r='+str(r)+'&g='+str(g)+'&b='+str(b))
	waitDone()

def motor(L,R):
	request('do/motor?L='+str(L)+'&R='+str(R))
	waitDone()
