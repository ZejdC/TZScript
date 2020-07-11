import mouse as m
import time as t
import platform
from win32api import GetSystemMetrics
import paho.mqtt.client as mqtt
import threading

TOPICMOVEMENT = "tzmouse/"+platform.node()
TOPICLMBPRESS = "tzmouse/LMBPress/"+platform.node()
TOPICRMBPRESS = "tzmouse/RMBPress/"+platform.node()
TOPICLMBCLICK = "tzmouse/LMBClick/"+platform.node()
TOPICRMBCLICK = "tzmouse/RMBClick/"+platform.node()
TOPICSCROLLUP = "tzmouse/ScrollUp/"+platform.node()
TOPICSCROLLDW = "tzmouse/ScrollDown/"+platform.node()

ubrzavajx = 0
ubrzavajy = 0
treshold = 0.001
primio = True
ignorisi = True

duration = 1
press = False
coefx = 1*GetSystemMetrics(0)/2
coefy = 1*GetSystemMetrics(1)/5
xvelocity = 0.
yvelocity = 0.
maksx=0.
maksy=0.
trenjekoef = 5
pozitivnoX = 0
pozitivnoY = 0

greskax = 0.
greskay = 0.

tracker = open("data.txt","w")
brojac = 0

def provjeraprvaporuka():
    global primio
    global ignorisi

    while True:

        t.sleep(0.3)


def funkcijatrenja():
    global xvelocity
    global yvelocity
    global pozitivnoY
    global pozitivnoX
    global ubrzavajx
    global ubrzavajy
    global ignorisi

    global greskax
    global greskay
    while True:
        if xvelocity>treshold:
            ubrzavajx = 1
        elif xvelocity<-treshold:
            ubrzavajx = -1
        else:
            ubrzavajx = 0
        if yvelocity>treshold:
            ubrzavajy = 1
        elif yvelocity<-treshold:
            ubrzavajy = -1
        else:
            ubrzavajy=0

        if ubrzavajy==0 and ubrzavajx==0:
            ignorisi = False
        else:
            ignorisi = False
        xvelocity = xvelocity/trenjekoef
        yvelocity = yvelocity/trenjekoef

        #print(xvelocity.__round__(2).__str__())
        #print("X:"+ubrzavajx.__str__()+"Y:"+ubrzavajy.__str__())
        #print(xvelocity.__round__(2).__str__()+ " "+ yvelocity.__round__(2).__str__())
        #print(greskax.__str__()+" "+greskay.__str__())


        t.sleep(0.2)
def velocityx(acceleration):
    global  xvelocity
    return xvelocity + acceleration*duration
def velocityy(acceleration):
    global yvelocity
    return yvelocity + acceleration*duration

def giveDistanceX(x):
    return coefx * xvelocity*duration + (x*duration*duration)/2


def giveDistanceY(y):
    return coefx * yvelocity*duration + (y*duration*duration)/2


def moveCursor(x, y, abs):
    global xvelocity
    global yvelocity
    global pozitivnoY
    global pozitivnoX

    global greskax
    global greskay

    global primio


    movex = 0.
    movey = 0.

    if ubrzavajx==0 or (ubrzavajx==1 and x > 0) or (ubrzavajx==-1 and x < 0):
        movex = giveDistanceX(x)
    if ubrzavajy==0 or (ubrzavajy==1 and y > 0) or (ubrzavajy==-1 and y < 0):
        movey = giveDistanceY(y)
    greskax = greskax+x
    greskay = greskay+y

    xvelocity = velocityx(x)
    yvelocity = velocityy(y)

    # print("([" + xvelocity.__round__(2).__str__() + "," + yvelocity.__round__(2).__str__() + "],[" + x.__round__(2).__str__() + "," +
    #       y.__round__(2).__str__() + "]) -> (" + movex.__str__() + "," + movey.__str__() + ")")

    m.move(movex, movey, abs,0.2)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    string = "tzmouse/#"
    name = platform.node()
    client.subscribe(string)
    print("Subsribed on "+string)

def on_message(client, userdata, msg):
    global maksy
    global maksx
    global brojac
    global tracker
    global press
    global ignorisi

    global primio
    poruka = msg.payload.decode()
    #print(poruka +" " + msg.topic)
    if msg.topic == TOPICMOVEMENT:
        primio = True
        if ignorisi:
            return
        niz = poruka.split(",")
        accx = -float(niz[0])
        accy = float(niz[1])
        if accx>maksx:
            maksx=accx
        if accy>maksy:
            maksy=accy
        with open('data.txt', 'a') as the_file:
            the_file.write(brojac.__str__()+"\t"+accx.__str__()+"\t"+accy.__str__()+"\n")
        brojac = brojac + 1
        print(accx.__str__()+"\t"+accy.__str__())
        moveCursor(accx,accy,False)
    elif msg.topic == TOPICLMBCLICK:
        m.click()
    elif msg.topic == TOPICRMBCLICK:
        m.right_click()
    elif msg.topic == TOPICLMBPRESS:
        poruka = msg.payload.decode()
        broj = int(poruka)
        if broj == 1 and not press:
            press = True
            m.press()
        elif broj == 0 and press:
            press = False
            m.release()
    elif msg.topic == TOPICSCROLLUP:
        m.wheel(1)
    elif msg.topic == TOPICSCROLLDW:
        m.wheel(-1)
    primio = False

def on_disconnect():
    print(maksx)
    print(maksy)

trenje_nit = threading.Thread(target=funkcijatrenja)
trenje_nit.start()

primljena_nit = threading.Thread(target=provjeraprvaporuka)
#primljena_nit.start()

client = mqtt.Client()
client.connect("broker.hivemq.com",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
