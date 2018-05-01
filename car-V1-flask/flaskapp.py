from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

import http.client

from main import *
from melody import Melody

import json
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

Data = {'id':0,
		'isEnable':True,
		'led':{'r':0,'g':0,'b':0},
		'motor':[0,0,0,0],
		'temp':0,
		'humi':0,
		'sound':{'melody':0,'melodykey':'','duration':4},
		'location':{'x':0,'y':0,'direction':0},
		'action':'' }

minSpeed = 600
maxSpeed = 999

# MARK : Local Service
def led(r,g,b):
	Data['led']['r'] = r
	Data['led']['g'] = g
	Data['led']['b'] = b

def sound(melody):
	global Data
	if melody in Melody:
		Data['sound']['melodykey'] = melody
		Data['sound']['melody'] = Melody[melody]
	else:
		Data['sound']['melody'] = 0
	Data['sound']['duration'] = 4

soundRunner = 0
def sounds(notes):
	global soundRunner
	noteArray = notes.split(' ')
	sound(noteArray[soundRunner])
	soundRunner += 1
	if soundRunner == len(noteArray):
		soundRunner = 0


fieldHeight = 1000
fieldWidth 	= 1000
TargetX = -1 # Don't Go
TargetY = -1 # Don't Go
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
		TargetX = -1
		TargetY = -1
		return
	system_goto(TargetX,TargetY)
def system_goto(x,y):
	maxError = 5
	differentX = x - Data['location']['x']
	differentY = y - Data['location']['y']
	if math.fabs(differentX) < maxError and math.fabs(differentY) < maxError:
		stop()
		return
	else:
		Data['action'] = 'goto'

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

TargetDirection = 0
def rotate(direction):
	TargetDirection = direction
	system_rotate(TargetDirection)
def system_rotate(direction):
	maxError = 5
	differentDirection = direction - Data['location']['direction']
	if math.fabs(differentDirection) < maxError:
		stop()
		return
	else:
		Data['action'] = 'rotate'
		if differentDirection > 0:
			motor(-minSpeed,minSpeed)
		else:
			motor(minSpeed,-minSpeed)

def stop():
	Data['action'] = ''
	motor(0,0)
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
		Data['motor'][3] = -L
	else:
		Data['motor'][2] = L
		Data['motor'][3] = 0

def humi():
	return Data['humi']
def temp():
	return Data['temp']

# MARK : Server Service
locationHostIP = "192.168.1.12"
def requestServer(path):
	connection = http.client.HTTPConnection(locationHostIP)
	connection.request("GET",path)
	response = connection.getresponse()
	data = response.read().decode("utf-8") 
	connection.close()
	return data

def request_location():
	rawLocation = json.loads(request('/location'))
	Data['location']['x'] = rawLocation[Data['id']]['x']
	Data['location']['y'] = rawLocation[Data['id']]['y']
	Data['location']['direction'] = rawLocation[Data['id']]['theta']

@app.route('/')
def update_data_to_mcu():
	global Data
	Data['humi'] = request.args.get('humi') if int(request.args.get('humi')) < 100 else Data['humi']
	Data['temp'] = request.args.get('temp') if int(request.args.get('temp')) < 100 else Data['temp']
	loop()
	update()
	if Data['action'] == 'goto':
		system_goto(TargetX,TargetY)
	elif Data['action'] == 'rotate':
		system_rotate(TargetDirection)
	return(
		("{0:0=3d}".format(Data['motor'][0]))+
		("{0:0=3d}".format(Data['motor'][1]))+
		("{0:0=3d}".format(Data['motor'][2]))+
		("{0:0=3d}".format(Data['motor'][3]))+
		("{0:0=3d}".format(Data['led']['r']))+
		("{0:0=3d}".format(Data['led']['g']))+
		("{0:0=3d}".format(Data['led']['b']))+
		("{0:0=4d}".format(Data['sound']['melody']))+
		("{0:0=1d}".format(Data['sound']['duration'])) )

@app.route('/control')
def control():
	return render_template('home.html', 
		ledR=Data['led']['r'], 
		ledG=Data['led']['g'], 
		ledB=Data['led']['b'], 
		humi=Data['humi'], 
		temp=Data['temp'],
		melody=Data['sound']['melodykey'] )

@socketio.on('updates')
def update_data_from_web(message):
	global Data
	inputs = message.split(",")
	Data['motor'][0] = int(inputs[0])
	Data['motor'][1] = int(inputs[1])
	Data['motor'][2] = int(inputs[2])
	Data['motor'][3] = int(inputs[3])
	Data['led']['r'] = int(inputs[4])
	Data['led']['g'] = int(inputs[5])
	Data['led']['b'] = int(inputs[6])
	sound(inputs[7])
	update()

def update():
	socketio.emit('status', json.dumps(Data) , broadcast=True)

@socketio.on('request')
def manual_request(message):
	socketio.emit('status', json.dumps(Data) , broadcast=True)

# MARK : Service Version2
@app.route('/do/standby')
def do_standby():
	return( "OK" if Data['action'] == '' else "NO" )
@app.route('/do/led')
def do_led():
	global Data
	Data['led']['r'] = int(request.args.get('r'))
	Data['led']['g'] = int(request.args.get('g'))
	Data['led']['b'] = int(request.args.get('b'))
	update()
	return( "OK" )
@app.route('/do/motor')
def do_motor():
	global Data
	L = int(request.args.get('L'))
	R = int(request.args.get('R'))
	motor(L,R)
	update()
	return( "OK" )