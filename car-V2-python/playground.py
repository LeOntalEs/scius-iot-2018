from time import sleep
import library as Toy
Toy.offsensor()

try:
    
    Toy.rotate(350)
    while True:
        Toy.motor(-999, -999)
        sleep(0.5)
finally:
    Toy.stop()

# while True:
#     step = 5
#     delay = 0.001
#     for c in range(3):
#         intens = [0, 0, 0]
#         for i in range(0, 255, step):
#             intens[c] = i
#             Toy.led(*intens)
#         for i in range(255, 0, -step):
#             intens[c] = i
#             Toy.led(*intens)

