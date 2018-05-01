from turtle import *

def tree(size):
    left(90)
    init_pos=pos()
    init_head=heading()
    forward(size*0.5)
    left(45)
    for i in range(3):
        branch(size*0.5)
        right(45)
    setpos(init_pos)
    setheading(init_head)
def branch(size):
    init_pos=pos()
    init_head=heading()
    forward(size*0.75)
    left(45)
    for i in range(3):
        leaf(size*0.25)
        right(45)
    setpos(init_pos)
    setheading(init_head)
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

tree(50)




exitonclick()