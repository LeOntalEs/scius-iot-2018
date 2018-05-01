from turtle import *

def leaf(size):
    init_pos=pos()
    init_head=heading()
    forward(size)
    left(30)
    for i in range(3):
        forward(size)
        right(120)
    setpos(init_pos)
    setheading(init_head)
    
leaf(100)





exitonclick()