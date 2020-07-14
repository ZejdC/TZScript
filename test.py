import mouse as m
import platform
import paho.mqtt.client as mqtt

TOPICMOVEMENT = "tzmouse/" + platform.node()
TOPICLMBPRESS = "tzmouse/LMBPress/" + platform.node()
TOPICRMBPRESS = "tzmouse/RMBPress/" + platform.node()
TOPICLMBCLICK = "tzmouse/LMBClick/" + platform.node()
TOPICRMBCLICK = "tzmouse/RMBClick/" + platform.node()
TOPICSCROLLUP = "tzmouse/ScrollUp/" + platform.node()
TOPICSCROLLDW = "tzmouse/ScrollDown/" + platform.node()

press = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    string = "tzmouse/#"
    client.subscribe(string)
    print("Subsribed on " + string)


metertopixelratio = 3779.52755905


def on_message(client, userdata, msg):
    global maksy
    global maksx
    global brojac
    global press

    poruka = msg.payload.decode()
    print(poruka + "\t" + msg.topic)
    if msg.topic == TOPICMOVEMENT:
        niz = poruka.split(",")
        x = float(niz[0]) * metertopixelratio
        y = 0
        m.move(x, y, False)
    elif msg.topic == TOPICLMBCLICK:
        m.click()
    elif msg.topic == TOPICRMBCLICK:
        m.right_click()
    elif msg.topic == TOPICLMBPRESS:
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
client.connect("broker.hivemq.com", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
