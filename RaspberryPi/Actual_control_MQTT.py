import paho.mqtt.client as mqtt
import time
from gpiozero import LED,Button,Motor,PWMLED

PUL = PWMLED(23)
DIR = LED(24)
ENA = LED(25)
motor = Motor(12,16)
NC = LED(20)
C = Button(21)
NC.on()
DIR.on()
ENA.on()
PUL.value = 0.5

def on_connect(client,userdata,flags,rc):
    if rc == 0:
        #User Interface
        print("Client is connected")
        print("What do you want to do?")
        print("        Motor                           Stepper motor")    
        print("Type MotorFW -> Forward motor  Type StepperFW -> Forward motor")
        print("Type MotorBW -> Backward motor Type StepperBW -> Backward motor")
        print("Type StopMotor -> Stop motor   Type StopStepper -> Stop motor\nType Exit -> Exit program")       
        global connected
        connected = True
    else:
        print("Client is not connected")
def on_message(client,userdata,message):
    global Msg,Messagerecieved
    Msg = message.payload.decode("utf-8")
    print(str(Msg))
    #Motor control
    if Msg == "MotorFW":
        time.sleep(1)
        motor.forward()
        print("Motor Forward")
    elif Msg == "MotorBW":
        time.sleep(1)
        motor.backward()
        print("Motor Backward")
    elif Msg == "StopMotor":
        time.sleep(1)
        motor.stop()
        print("Stop motor")
    #Stepper motor control
    elif Msg == "StepperFW":
        ENA.on()
        time.sleep(1)
        ENA.off()
        print("Stepper Motor Forward")
    elif Msg == "StepperBW":
        ENA.on()
        time.sleep(1)
        DIR.off()
        ENA.off
        print("Stepper Motor Backward")
    elif Msg == "StopStepper":
        ENA.on()
        DIR.on()
        print("Stepper Motor Stop")
    #Exit program
    elif Msg == "Exit":
        print("Exit program")
        Messagerecieved = True
    else:
        print("Not Found")
    
C.when_pressed = print("Switch on")
C.when_released = print("Switch off")

connected = False
Messagerecieved = False

broker = "161.200.199.2"
port = 1883

client = mqtt.Client("MQTT")
client.on_message = on_message
client.on_connect = on_connect
client.connect(broker,port = port)
client.loop_start()
client.subscribe("Topic") #can change topic to other name
while connected != True:
    time.sleep(1)
while Messagerecieved != True:
    time.sleep(1)
client.loop_stop()
