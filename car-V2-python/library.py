from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit
import http.client

from melody import Melody

import json
import math
from time import sleep # sleep(second)

##### EDIT HEAR #####
ID = '18'				# Your ID
secret = '18'			# Your Secret
#####################

isPrintAction = True
def printAction(message):
	if isPrintAction:
		print(message)

Data = {'isEnable':True,
		'led':{'r':0,'g':0,'b':0},
		'motor':[0,0,0,0],
		'temp':0,
		'humi':0,
		'sound':{'melody':0,'melodykey':'','duration':4},
		'location':{'x':0,'y':0,'direction':0} }

minSpeed = 600
maxSpeed = 999

dhtEnable = False

# MARK : Local Service
def led(r,g,b):
	Data['led']['r'] = r
	Data['led']['g'] = g
	Data['led']['b'] = b
	printAction('[car] LED - R:'+str(r)+' G:'+str(g)+' B:'+str(b))
	upload()

def sound(melody):
	global Data
	if melody in Melody:
		Data['sound']['melodykey'] = melody
		Data['sound']['melody'] = Melody[melody]
	else:
		Data['sound']['melody'] = 0
		printAction('[car] Sound - Melody Incorrect')
		return
	Data['sound']['duration'] = 4
	printAction('[car] Sound - Melody:'+str(melody))
	upload()

def sounds(notes):
	noteArray = notes.split(' ')
	for note in noteArray:
		sound(note)
		sleep(0.4)


fieldHeight = 1000
fieldWidth 	= 1000
def directionFromPoint(x,y):
	differentX = x - Data['location']['x']
	differentY = y - Data['location']['y']
	if differentX == 0 and differentY == 0:
		targetDirection = 0
	elif differentX == 0:
		if differentY >= 0:
			targetDirection = 90
		else:
			targetDirection = 270
	elif differentY == 0:
		if differentX >= 0:
			targetDirection = 0
		else:
			targetDirection = 180
	else:
		targetDirection = math.atan(differentY/differentX) * (180/math.pi)
		if 	 differentX > 0 and differentY > 0: #Q1
			pass
		elif differentX < 0 and differentY > 0: #Q2
			targetDirection += 90
		elif differentX < 0 and differentY < 0: #Q3
			targetDirection += 180
		elif differentX > 0 and differentY < 0: #Q4
			targetDirection += 360
	return targetDirection
def goto(x,y):
	global TargetX,TargetY
	# Protection
	if ((x >= 0 and x <= fieldWidth) and (y >= 0 and y <= fieldHeight)):
		TargetX = x
		TargetY = y
	else:
		return
	maxError = 5
	differentX = x - Data['location']['x']
	differentY = y - Data['location']['y']
	while math.fabs(differentX) > maxError and math.fabs(differentY) > maxError:
		targetDirection = directionFromPoint(x,y)
		differentDirection = targetDirection - Data['location']['direction']
		# Speed
		rangeSpeed 	= maxSpeed - minSpeed
		targetSpeed = maxSpeed - (rangeSpeed*(differentDirection/90))
		# Action
		if differentDirection > 0:
			motor(targetSpeed,maxSpeed)
		else:
			motor(maxSpeed,targetSpeed)
		# Update
		sleep(0.5)
		update()
		differentX = x - Data['location']['x']
		differentY = y - Data['location']['y']

def rotate(direction):
	maxError = 5
	differentDirection = direction - Data['location']['direction']
	while math.fabs(differentDirection) > maxError:
		if differentDirection > 0:
			motor(-minSpeed,minSpeed)
		else:
			motor(minSpeed,-minSpeed)
		sleep(0.5)
		update()
		differentDirection = direction - Data['location']['direction']

def stop():
	motor(0,0)
	upload()
def motor(L,R): # L,R is (Int) -999(maxSpeed) to 999(maxSpeed)
	# Protection
	if L < -maxSpeed:
		L = -maxSpeed
	elif L > maxSpeed:
		L = maxSpeed
	if R < -maxSpeed:
		R = -maxSpeed
	elif R > maxSpeed:
		R = maxSpeed
	# Action
	if L < 0:
		Data['motor'][0] = 0
		Data['motor'][1] = -L
	else:
		Data['motor'][0] = L
		Data['motor'][1] = 0
	if R < 0:
		Data['motor'][2] = 0
		Data['motor'][3] = -R
	else:
		Data['motor'][2] = R
		Data['motor'][3] = 0
	printAction('[car] Motor - L:'+str(L)+' R:'+str(R))
	upload()

def humi():
	printAction('[car] Humi '+str(Data['humi'])+' %')
	return Data['humi']
def temp():
	printAction('[car] Temp '+str(Data['temp'])+' *c')
	return Data['temp']

def offsensor():
	global dhtEnable
	dhtEnable = False
	upload()

def onsensor():
	global dhtEnable
	dhtEnable = True
	upload()

# MARK : Server Service
locationHostIP = "192.168.1.99:8000"
def requestServer(path):
	connection = http.client.HTTPConnection(locationHostIP)
	connection.request("GET",path)
	response = connection.getresponse()
	data = response.read().decode("utf-8") 
	connection.close()
	return data

def upload():
	dataForSend =str(("{0:0=3d}".format(Data['motor'][0]))+
					("{0:0=3d}".format(Data['motor'][1]))+
					("{0:0=3d}".format(Data['motor'][2]))+
					("{0:0=3d}".format(Data['motor'][3]))+
					("{0:0=3d}".format(Data['led']['r']))+
					("{0:0=3d}".format(Data['led']['g']))+
					("{0:0=3d}".format(Data['led']['b']))+
					("{0:0=4d}".format(Data['sound']['melody']))+
					("{0:0=1d}".format(Data['sound']['duration']))+
					("{0:0=1d}".format(dhtEnable)) )
	requestServer('/setcmd/'+str(ID)+'/'+secret+'/'+dataForSend+'/')

def update():
	global Data
	printAction('[car] request...')
	rawData = json.loads(requestServer('/getstatus/'))
	Data['location']['x'] = rawData[ID]['x']
	Data['location']['y'] = rawData[ID]['y']
	Data['location']['direction'] = rawData[ID]['theta']
	Data['temp'] = rawData[ID]['temp']
	Data['humi'] = rawData[ID]['humi']
