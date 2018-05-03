import library as car

try:
    car.offsensor()
    car. goto(300, 150, 700, 700)
    car.update()
    print(car.getx(car.ID), car.gety(car.ID))
    # car.rotate(270, 700)

    # while(True):
    #     car.update()
    #     print(car.getx(4))
    #     print(car.gety(4))
    #     print(car.getdegree(4))
    #     print()
finally:
    car.reset()
