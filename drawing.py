from turtle import *

def draw_concentric_circles():
    import turtle

    t = turtle.Turtle()
    screen = turtle.Screen()
    screen.bgcolor("white")
    t.speed(6)
    t.pensize(2)

    colors = ["red", "blue", "green", "purple", "orange"]

    for i in range(5): 
        t.pencolor(colors[i])
        t.penup()
        t.goto(0, -20 * i) 
        t.pendown()
        t.circle(20 * (i + 1))

    t.hideturtle()
    turtle.done()

    exitonclick()

def draw_cloud():
    import turtle as t
    screen = t.Screen()
    screen.bgcolor('skyblue')
    t.speed(5)
    t.pensize(2)

    t.fillcolor('white')
    t.pencolor('white')

    t.penup()
    t.goto(0, 0)
    t.pendown()
    t.begin_fill()
    t.circle(40)
    t.end_fill()

    t.penup()
    t.goto(-50, 20)
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()

    t.penup()
    t.goto(50, 20)
    t.pendown()
    t.begin_fill()
    t.circle(30)
    t.end_fill()

    t.penup()
    t.goto(-40, -20)
    t.pendown()
    t.begin_fill()
    t.circle(25)
    t.end_fill()

    t.penup()
    t.goto(40, -20)
    t.pendown()
    t.begin_fill()
    t.circle(25)
    t.end_fill()

    t.hideturtle()
    turtle.done()

    t.done()

    exitonclick()  # EXIST


print("----- Welcome to the drawing system ----")
while True:
    a = input("---- Please select what you want to draw:\n"
              " (1 for cloud, 2 for concentric circles)\n"
              "Your selection is: ")
    try:
        a = eval(a)
        if a == 1:
            draw_cloud()
        elif a == 2:
            draw_concentric_circles()
        else:
            print("Please input the value in [1,2]")
    except:
        print("Please input the value in [1,2]")


