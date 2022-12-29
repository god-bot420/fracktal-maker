#generate random complex fractal designs in tutle to fill up whole screen

import turtle
import random

def draw_fractal(t, size):
    if size < 5:
        return
    else:
        t.forward(size)
        t.left(30)
        draw_fractal(t, size - 10)
        t.right(60)
        draw_fractal(t, size - 10)
        t.left(30)
        t.backward(size)

def main():
    t = turtle.Turtle()
    my_win = turtle.Screen()
    t.left(90)
    t.up()
    t.backward(200)
    t.down()
    t.color("blue")
    draw_fractal(t, 100)
    my_win.exitonclick()

main()



