from turtle import *
color('red', 'yellow')

def tri(size):
    for i in range(3):
        forward(size)
        right(120)

tri(150)

exitonclick()