from flask import Flask, request, render_template
import datetime
import json
from awscrt import mqtt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

DEVICE_CONFIGS = {
    "lightBrightness": 100,
    "curtainPercentage": 0,
    "thermostatTemperature": 20,
    "thermostatMode": 'cold'
}

MQTT_CLIENTS = {}

app = Flask(__name__)

@app.route("/")
def index():
    global DEVICE_CONFIGS
    return render_template("simulator.html")


@app.route("/simulation")
def simulation():
    global DEVICE_CONFIGS
    return render_template("simulationEnv.html", devices=DEVICE_CONFIGS)


@app.route("/controller", methods=["GET", "POST"])
def controller():
    global DEVICE_CONFIGS
    if request.method == "GET":
        return render_template("controller.html", deviceData=DEVICE_CONFIGS)

    if request.method == "POST":
        RESPONSE_OBJ = {
            "status": "Unknown",
            "message": "Unknown",
            "username": None,
            "room": None,
            "usedConfig": {
                "light": {
                    "lightIntensity": None,
                    "status": None
                },
                "thermostat": {
                    "thermostatTemperature": None,
                    "thermostatMode": None,
                    "status": None
                },
                "curtain": {
                    "curtainPercentage": None,
                    "status": None
                }
            }
        }
        RESPONSE_CODE = 400
        data = json.loads(request.data)
        lightIntensity = data.get("lightIntensity")
        thermostatTemp = data.get("thermostatTemperature")
        thermostatMode = data.get("thermostatMode")
        curtainPercentage = data.get("curtainPercentage")

        username = data.get("username")
        room = data.get("room")
        PassedUpdates = []
        
        RESPONSE_OBJ["username"] = username
        RESPONSE_OBJ["room"] = room
        RESPONSE_OBJ["usedConfig"]["light"]["lightIntensity"] = lightIntensity
        RESPONSE_OBJ["usedConfig"]["thermostat"]["thermostatTemperature"] = thermostatTemp
        RESPONSE_OBJ["usedConfig"]["thermostat"]["thermostatMode"] = thermostatMode
        RESPONSE_OBJ["usedConfig"]["curtain"]["curtainPercentage"] = curtainPercentage
        
        NumberOFRequestedUpdates = 0
        if lightIntensity is not None:
            NumberOFRequestedUpdates += 1
        else:
            # remove the key from the dict
            RESPONSE_OBJ["usedConfig"].pop("light")
        if thermostatTemp is not None or thermostatMode is not None:
            NumberOFRequestedUpdates += 1
        else:
            # remove the key from the dict
            RESPONSE_OBJ["usedConfig"].pop("thermostat")
        if curtainPercentage is not None:
            NumberOFRequestedUpdates += 1
        else:
            # remove the key from the dict
            RESPONSE_OBJ["usedConfig"].pop("curtain")

        
        if username is None:
            RESPONSE_OBJ["status"] = "Failed"
            RESPONSE_OBJ["message"] = "Username is required"
            # remove the key from the dict
            RESPONSE_OBJ.pop("username")
            RESPONSE_OBJ.pop("room")
            RESPONSE_OBJ.pop("usedConfig")
            RESPONSE_CODE = 400
            return json.dumps(RESPONSE_OBJ), RESPONSE_CODE, {'ContentType': 'application/json'}

        if room is None:
            RESPONSE_OBJ["status"] = "Failed"
            RESPONSE_OBJ["message"] = "Room is required"
            # remove the key from the dict
            RESPONSE_OBJ.pop("username")
            RESPONSE_OBJ.pop("room")
            RESPONSE_OBJ.pop("usedConfig")
            RESPONSE_CODE = 400
            return json.dumps(RESPONSE_OBJ), RESPONSE_CODE, {'ContentType': 'application/json'}

        username = data["username"]
        room = data["room"]
        
        RESPONSE_OBJ["username"] = username
        RESPONSE_OBJ["room"] = room

        if lightIntensity != None:
            lightIntensity = int(lightIntensity)
            if lightIntensity != DEVICE_CONFIGS["lightBrightness"]:
                # validate lightIntensity
                if lightIntensity < 0 or lightIntensity > 100:
                    RESPONSE_OBJ["usedConfig"]["light"]["message"] = "lightIntensity must be between 0 and 100"
                    RESPONSE_OBJ["usedConfig"]["light"]["status"] = "Failed"
                else:
                    # call function to turn on/off light
                    try :
                        lightControl(lightIntensity, username, room)
                        RESPONSE_OBJ["usedConfig"]["light"]["status"] = "Success"
                        PassedUpdates.append("light")
                    except:
                        RESPONSE_OBJ["usedConfig"]["light"]["status"] = "Failed"

        if thermostatTemp != None or thermostatMode != None:
            if thermostatTemp is None:
                thermostatTemp = DEVICE_CONFIGS["thermostatTemperature"]
            if thermostatMode is None:
                thermostatMode = DEVICE_CONFIGS["thermostatMode"]
            
            thermostatTemp = int(thermostatTemp)
            if thermostatTemp != DEVICE_CONFIGS["thermostatTemperature"] or thermostatMode != DEVICE_CONFIGS["thermostatMode"]:
                
                # Validate temperature
                if thermostatTemp > 100 or thermostatTemp < -10:
                    RESPONSE_OBJ["usedConfig"]["thermostat"]["message"] = "Temperature is out of range"
                    RESPONSE_OBJ["usedConfig"]["thermostat"]["status"] = "Failed"
                elif thermostatMode != "cold" and thermostatMode != "heat":
                    RESPONSE_OBJ["usedConfig"]["thermostat"]["message"] = "Thermostat mode is not valid"
                    RESPONSE_OBJ["usedConfig"]["thermostat"]["status"] = "Failed"
                else:
                    # call function to  set thermostat
                    try:
                        thermoControl(thermostatMode, thermostatTemp, username, room)
                        RESPONSE_OBJ["usedConfig"]["thermostat"]["status"] = "Success"
                        PassedUpdates.append("thermostat")
                    except:
                        RESPONSE_OBJ["usedConfig"]["thermostat"]["status"] = "Failed"

        if curtainPercentage != None:
            curtainPercentage = int(curtainPercentage)
            if curtainPercentage != DEVICE_CONFIGS["curtainPercentage"]:
                # validate curtainPercentage
                if curtainPercentage < 0 or curtainPercentage > 100:
                    RESPONSE_OBJ["usedConfig"]["curtain"]["message"] = "Curtain Open Percentage must be between 0 and 100"
                    RESPONSE_OBJ["usedConfig"]["curtain"]["status"] = "Failed"
                else:
                    # call function to close curtain
                    try:
                        curtainControl(curtainPercentage, username, room)
                        RESPONSE_OBJ["usedConfig"]["curtain"]["status"] = "Success"
                        PassedUpdates.append("curtain")
                    except:
                        RESPONSE_OBJ["usedConfig"]["curtain"]["status"] = "Failed"
                    
        if len(PassedUpdates) == 0:
            RESPONSE_OBJ["status"] = "Failed"
            RESPONSE_OBJ["message"] = "Failed to update devices"
            RESPONSE_CODE = 400
        elif len(PassedUpdates) == 3:
            RESPONSE_OBJ["status"] = "Success"
            RESPONSE_OBJ["message"] = "All devices updated successfully"
            RESPONSE_CODE = 200
        elif len(PassedUpdates) > 0:
            RESPONSE_OBJ["status"] = "Partial Success"
            RESPONSE_OBJ["message"] = "Successfully few devices"
            RESPONSE_CODE = 200

        #return request with mimetype='application/json'
        return json.dumps(RESPONSE_OBJ), RESPONSE_CODE, {'Content-Type': 'application/json'}
        

    return "Invalid Request!", 500


def lightControl(intensity, username, room):
    client = MQTT_CLIENTS["myMQTTClientLight"]
    data = {}
    if intensity != 0:
        data["light-on"] = intensity
    else:
        data["light-on"] = 0
    data["username"] = username
    data["room_name"] = room
    client.publish(topic="trigger/light_on",
                   payload=json.dumps(data), QoS=mqtt.QoS.AT_LEAST_ONCE)


def curtainControl(percentage, username, room):
    client = MQTT_CLIENTS["myMQTTClientLight"]
    data = {}
    data["curtain-open"] = percentage
    data["username"] = username
    data["room_name"] = room
    client.publish(topic="trigger/curtain_open",
                   payload=json.dumps(data), QoS=mqtt.QoS.AT_LEAST_ONCE)


def thermoControl(mode, temperature, username, room):
    client = MQTT_CLIENTS["myMQTTClientLight"]
    data = {}
    data["temperature"] = temperature
    data["thermostatMode"] = "heat" if mode != 'cold' else "cold"
    data["username"] = username
    data["room_name"] = room
    client.publish(topic="trigger/thermostat_update",
                   payload=json.dumps(data), QoS=mqtt.QoS.AT_LEAST_ONCE)


def customCallbackLight(client, userData, message):
    global DEVICE_CONFIGS
    data = json.loads(message.payload)

    username = data["username"]
    room_name = data["room_name"]
    print(">>> In room: " + room_name + " of user: " + username, end="\n")

    time = datetime.datetime.now()
    print(time, end=" ")
    if data["light-on"] > 0:
        DEVICE_CONFIGS["lightBrightness"] = data["light-on"]
        print("--- LIGHT TURNED ON with intensity = {}".format(data["light-on"]))

    elif data["light-on"] == 0:
        DEVICE_CONFIGS["lightBrightness"] = 0
        print("--- LIGHT TURNED OFF")


def customCallbackThermo(client, userData, message):
    global DEVICE_CONFIGS
    data = json.loads(message.payload)

    username = data["username"]
    room_name = data["room_name"]
    print(">>> In room: " + room_name + " of user: " + username, end="\n")

    time = datetime.datetime.now()
    print(time, end=" ")
    if data["thermostatMode"] == "heat":
        DEVICE_CONFIGS["thermostatMode"] = "heat"
        DEVICE_CONFIGS["thermostatTemperature"] = int(data["temperature"])
        print(
            "--- Heater status = ON with Temperature = {}".format(data["temperature"]))
    elif data["thermostatMode"] == "cold":
        DEVICE_CONFIGS["thermostatMode"] = "cold"
        DEVICE_CONFIGS["thermostatTemperature"] = int(data["temperature"])
        print(
            "--- Cooler status = ON with Temperature = {}".format(data["temperature"]))


def customCallbackCurtain(client, userData, message):
    global DEVICE_CONFIGS
    data = json.loads(message.payload)

    username = data["username"]
    room_name = data["room_name"]
    print(">>> In room: " + room_name + " of user: " + username, end="\n")

    time = datetime.datetime.now()
    print(time, end=" ")
    curtain_open_percent = data["curtain-open"]

    if curtain_open_percent == 0:
        DEVICE_CONFIGS["curtainPercentage"] = 0
        print("--- CURTAIN CLOSED")
    else:
        DEVICE_CONFIGS["curtainPercentage"] = int(curtain_open_percent)
        print("--- CURTAIN OPEN Percentage = ", curtain_open_percent)


def devicesConnect():
    global MQTT_CLIENTS
    
    # create and configure a light_bulb client instance
    MQTT_CLIENTS["myMQTTClientLight"] = AWSIoTMQTTClient("light_bulb")    
    MQTT_CLIENTS["myMQTTClientLight"].configureEndpoint("a32yk77mbrevmu-ats.iot.us-east-2.amazonaws.com", 8883)
    MQTT_CLIENTS["myMQTTClientLight"].configureCredentials("./AmazonRootCA1.pem", "./private.pem.key", "./certificate.pem.crt")
    
    # create and configure a thermostat client instance
    MQTT_CLIENTS["myMQTTClientThermo"] = AWSIoTMQTTClient("thermostat")
    MQTT_CLIENTS["myMQTTClientThermo"].configureEndpoint("a32yk77mbrevmu-ats.iot.us-east-2.amazonaws.com", 8883)
    MQTT_CLIENTS["myMQTTClientThermo"].configureCredentials("./AmazonRootCA1.pem", "./private.pem.key", "./certificate.pem.crt")
    
    # create and configure a curtain client instance
    MQTT_CLIENTS["myMQTTClientCurtain"] = AWSIoTMQTTClient("curtain")
    MQTT_CLIENTS["myMQTTClientCurtain"].configureEndpoint("a32yk77mbrevmu-ats.iot.us-east-2.amazonaws.com", 8883)
    MQTT_CLIENTS["myMQTTClientCurtain"].configureCredentials("./AmazonRootCA1.pem", "./private.pem.key", "./certificate.pem.crt")

    # connect to AWS light_bulb IoT Client
    MQTT_CLIENTS["myMQTTClientLight"].connect()
    print("Device light_bulb Connected to server!")
    # subscribe to the `trigger/light_on` topic of the light_bulb client
    MQTT_CLIENTS["myMQTTClientLight"].subscribe("trigger/light_on", 1, customCallbackLight)

    # connect to AWS thermostat IoT Client
    MQTT_CLIENTS["myMQTTClientThermo"].connect()
    print("Device Thermostat Connected to server!")
    # subscribe to the `trigger/thermostat_update` topic of the thermostat client
    MQTT_CLIENTS["myMQTTClientThermo"].subscribe("trigger/thermostat_update", 1, customCallbackThermo)

    # connect to AWS curtain IoT Client
    MQTT_CLIENTS["myMQTTClientCurtain"].connect()
    print("Device Curtain Connected to server!")
    # subscribe to the `trigger/curtain_open` topic of the curtain client
    MQTT_CLIENTS["myMQTTClientCurtain"].subscribe("trigger/curtain_open", 1, customCallbackCurtain)


if __name__ == "__main__":
    devicesConnect()
    # set flask server port to 8000
    app.run(host="0.0.0.0", port=80, debug=True)
    exit = input()
