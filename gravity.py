import mouse as m
import platform
from win32api import GetSystemMetrics
import paho.mqtt.client as mqtt

TOPICMOVEMENT = "tzmouse/"+platform.node()
TOPICLMBPRESS = "tzmouse/LMBPress/"+platform.node()
TOPICRMBPRESS = "tzmouse/RMBPress/"+platform.node()
TOPICLMBCLICK = "tzmouse/LMBClick/"+platform.node()
TOPICRMBCLICK = "tzmouse/RMBClick/"+platform.node()
TOPICSCROLLUP = "tzmouse/ScrollUp/"+platform.node()
TOPICSCROLLDW = "tzmouse/ScrollDown/"+platform.node()

duration = 1
press = False
coefx = 1*GetSystemMetrics(0)/2
coefy = 1*GetSystemMetrics(1)/5

def giveDistanceX(x):
    global coefx
    return coefx * x


def giveDistanceY(y):
    global coefy
    return coefy * y


def moveCursor(x, y, abs):
    global xvelocity
    global yvelocity

    movex = giveDistanceX(x)
    movey = giveDistanceY(y)

    # print("([" + xvelocity.__round__(2).__str__() + "," + yvelocity.__round__(2).__str__() + "],[" + x.__round__(2).__str__() + "," +
    #       y.__round__(2).__str__() + "]) -> (" + movex.__str__() + "," + movey.__str__() + ")")

    m.move(movex, movey, abs,0.2)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    string = "tzmouse/#"
    client.subscribe(string)
    print("Subsribed on "+string)

def on_message(client, userdata, msg):
    global press
    poruka = msg.payload.decode()
    print(poruka +" " + msg.topic)
    if msg.topic == TOPICMOVEMENT:
        niz = poruka.split(",")
        accx = -float(niz[0])
        accy = float(niz[1])
        #print(accx.__str__()+"\t"+accy.__str__())
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

client = mqtt.Client()
client.connect("broker.hivemq.com",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
