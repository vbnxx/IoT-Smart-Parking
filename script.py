import RPi.GPIO as G
import time
import paho.mqtt.client as mqtt
import json

# GPIO Setup
G.setwarnings(False)
G.setmode(G.BCM)
TRIG = 23
ECHO = 24
TRESHOLD = 20
G.setup(TRIG, G.OUT)
G.setup(ECHO, G.IN)

#mqtt broker setup
BROKER = "localhost"
PORT = 1883
TOPIC = "parking/sensor"
CLIENT_ID = "P1"

client = mqtt.Client(CLIENT_ID)
client.connect(BROKER)
client.subscribe(TOPIC)

#measure distance function
def getDis(timeout=0.02):
    G.output(TRIG, False) #making sure that TRIG is low
    time.sleep(0.2) 

    G.output(TRIG, True)
    time.sleep(0.00001)
    G.output(TRIG, False)

    #wait until ECHO goes into high state (start of measurement)
    while G.input(ECHO) ==0:
        pulse_start = time.time()

    #wait until ECHO returns to a low state (end of measurement)
    while G.input(ECHO) == 1:
        pulse_end = time.time()

    #calculate the pulse duration
    pulse_duration = pulse_end - pulse_start

    distance = round((pulse_duration * 17150), 2)
    return distance

#main loop
try:
    while True:
        distance = getDis() #get the distance

        #check if parking spot is occupied or not
        if distance <= TRESHOLD:
            status = 'Parking spot 5 is occupied'
        else:
            status = "Parking spot 5 is available"
        payload = {
            "status": status,
            "distance": distance
        }

        #publish data to the MQTT broker
        client.publish(TOPIC, json.dumps(payload))
        print(f"published {payload} to topic: {TOPIC}")
        time.sleep(2) # wait 2 sec before taking next measurement

#Interrupt handling
except KeyboardInterrupt:
    print("Exiting..")
    G.cleanup()
    client.disconnect()