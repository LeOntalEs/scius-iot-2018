from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

from main import *
from melody import Melody

import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

Data = {'led':{'r':0,'g':0,'b':0},
		'motor':[0,0,0,0],
		'temp':0,
		'humi':0,
		'sound':{'melody':0,'melodykey':'','duration':1000},
		'location':{'x':0,'y':0,'direction':0}}

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


def goto(x,y):
	targetDirection = math.atan(y/x)
	# if targetDirection < Data['location']['direction']:
	# 	turnright()
	# elif targetDirection > Data['location']['direction']:
	# 	turnleft()
	# else:
	# 	if x != Data['location']['x'] or y != Data['location']['y']:
	# 		forward()
	# 	else:
	# 		stop()

def motor(L,R): # L,R is (Int) -999 to 999
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
@app.route('/')
def home():
	global Data
	Data['humi'] = request.args.get('humi') if int(request.args.get('humi')) < 100 else Data['humi']
	Data['temp'] = request.args.get('temp') if int(request.args.get('temp')) < 100 else Data['temp']
	loop()
	update()
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
def message(message):
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

app.route('/epoch')
