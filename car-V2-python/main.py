import library as car
from time import sleep # sleep(second)

# car.onsensor()		# Turn On Sensor
car.offsensor()			# Turn Off Sensor (Recommend)

	# # car.led(R,G,B) 		# R,G,B is (int) 0 to 255
# car.led(10,10,10)

	# # car.sound(melody) 	# melody is (String) [reference melody.py]
# car.sound('C6') 

	# # car.sounds(notes) 	# notes is (String) Sequence of melodys
# notes = "C6 C6 D6 C6 F6 E6 C6 C6 D6 C6 G6 F6 C6 C6 C7 A6 F6 E6 D6 C7 C7 B6 G6 A6 G6"
# car.sounds(notes)

# # car.update()		# Update X,Y,Theta,Temp,Humi from Server
# # car.temp() 			# return (int) Temperature
# # car.humi() 			# return (int) Humidity
	# #car.motor(L,R) 		# L,R is (int) -999 to 999
# car.motor(999,999) 	# forward
# car.motor(-999,-999) 	# backward
# car.motor(-999,999) 	# turnleft
# car.motor(999,-999) 	# turnright
# car.stop()			# stop
# sleep(1) 				# Sleep 1 second

