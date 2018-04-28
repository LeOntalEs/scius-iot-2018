from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

r = 0
g = 0
b = 0

m0 = 0
m1 = 0
m2 = 0
m3 = 0

@app.route('/')
def home():
	global r,g,b
	return(str(m0)+str(m1)+str(m2)+str(m3)+("{0:0=3d}".format(r))+("{0:0=3d}".format(g))+("{0:0=3d}".format(b)))

@app.route('/control')
def control():
	return render_template('home.html')

@socketio.on('c2s')
def message(message):
	emit('s2c',message, broadcast=True)
	print(message)

@socketio.on('updates')
def message(message):
	global r,g,b,m0,m1,m2,m3
	inputs = message.split(",")
	print(inputs)
	m0 = int(inputs[0])
	m1 = int(inputs[1])
	m2 = int(inputs[2])
	m3 = int(inputs[3])
	r = int(inputs[4])
	g = int(inputs[5])
	b = int(inputs[6])
	print(message)