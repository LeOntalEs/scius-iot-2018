from turtle import *
def leaf(size):
    forward(size)
    left(30)
    for i in range(3):
        forward(size)
        right(120)
        
leaf(100)





exitonclick()