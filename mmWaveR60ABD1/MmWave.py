import serial
import time
import paho.mqtt.client as mqtt
import random
import json

ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)

reset_frame = bytes([0x53, 0x59, 0x01, 0x02, 0x00, 0x01, 0x0F, 0xBF, 0x54, 0x43])

realtime_mode_frame = bytes([0x53, 0x59, 0x84, 0x0F, 0x00, 0x01, 0x00, 0x40, 0x54, 0x43])
sleepstatus_mode_frame = bytes([0x53, 0x59, 0x84, 0x0F, 0x00, 0x01, 0x01, 0x41, 0x54, 0x43])

HeartbeatPackageInquiry = bytes([0x53, 0x59, 0x01, 0x80, 0x00, 0x01, 0x0F, 0x3D, 0x54, 0x43])
ProductModel = bytes([0x53, 0x59, 0x02, 0xA1, 0x00, 0x01, 0x0F, 0x5F, 0x54, 0x43])

HumanDetectionSwitchOn = bytes([0x53, 0x59, 0x80, 0x00, 0x00, 0x01, 0x01, 0x2E, 0x54, 0x43])
HumanDetectionSwitchOff = bytes([0x53, 0x59, 0x80, 0x00, 0x00, 0x01, 0x00, 0x2D, 0x54, 0x43])

HeartRateSwitchOn = bytes([0x53, 0x59, 0x85, 0x00, 0x00, 0x01, 0x01, 0x33, 0x54, 0x43])
HeartRateSwitchOff = bytes([0x53, 0x59, 0x85, 0x00, 0x00, 0x01, 0x00, 0x32, 0x54, 0x43])

RespiratorySwitchOn = bytes([0x53, 0x59, 0x81, 0x00, 0x00, 0x01, 0x01, 0x2F, 0x54, 0x43])
RespiratorySwitchOff = bytes([0x53, 0x59, 0x81, 0x00, 0x00, 0x01, 0x00, 0x2E, 0x54, 0x43])

SleepSwitchOn = bytes([0x53, 0x59, 0x84, 0x00, 0x00, 0x01, 0x01, 0x32, 0x54, 0x43])
SleepSwitchOff = bytes([0x53, 0x59, 0x84, 0x00, 0x00, 0x01, 0x00, 0x31, 0x54, 0x43])

calibDuration = 20
refHeartRate = 60
totalRate = 0.0
numReadings = 0
avgRate = 0.0
calibrationFactor = 0.0

def mapping(x, in_min, in_max, out_min, out_max):
    run = in_max - in_min
    if run == 0:
        print("invalid input range")
        return -1
    rise = out_max - out_min
    delta = x - in_min
    return (delta * rise) // run + out_min

def readHeartRate(value):
    heartRate = mapping(value, 0, 100, 50, 100)
    return heartRate

def millis():
    return int(round(time.time() * 1000))

# Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Connection failed")
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")

# MQTT broker settings
broker_address = "10.253.1.54"
broker_port = 1883
username = "afhadmin"
password = "afhadmin"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
print(client_id)

# Create MQTT client instance
client = mqtt.Client(client_id) 

# Set username and password
client.username_pw_set(username, password)

# Assign callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect(broker_address, broker_port)

# Subscribe to topic
client.subscribe("/topic/test2")

# Start the MQTT loop
client.loop_start()

ser.write(HumanDetectionSwitchOff)
time.sleep(0.002)
ser.write(HeartRateSwitchOff)
time.sleep(0.002)
ser.write(RespiratorySwitchOff)
time.sleep(0.002)
ser.write(SleepSwitchOff)
time.sleep(0.002)

# ser.write(HumanDetectionSwitchOn)
# time.sleep(0.002)
ser.write(HeartRateSwitchOn)
time.sleep(0.002)
ser.write(RespiratorySwitchOn)
time.sleep(0.002)
# ser.write(SleepSwitchOn)
# time.sleep(0.002)

heartWave = []
breathWave = []
humanDist = []
humanPost = []
timeSoberSleep = []
timeLightSleep = []
timeDeepSleep = []
sleepState = []
sleepAnalys = []
heartValue = 0
breathValue = 0

infoBreath = ""

while True:

    data = ser.read(1)
    if data[0] == 0x53:
        data = ser.read(1)
        if data[0] == 0x59:
            data = ser.read(1)
            if data[0] == 0x85:#hearth data
                data = ser.read(1)
                if data[0] == 0x02:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            heartValue = ord(data) 
                            print("heartValue:", heartValue)
                elif data[0] == 0x05:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x05:
                            heartWave = []
                            for _ in range(5):
                                data = ser.read(1)
                                heartWave.append(data[0])
                            print("heart wave:", heartWave)
                            max_value = max(heartWave)
                            max_index = heartWave.index(max_value)
                            print(max_value)
                            print(max_index)

            elif data[0] == 0x81:#respiratory data
                data = ser.read(1)
                if data[0] == 0x02:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            breathValue = ord(data) 
                            print("breathValue:", breathValue)
                elif data[0] == 0x05:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x05:
                            breathWave = []
                            for _ in range(5):
                                data = ser.read(1)
                                breathWave.append(data[0])
                            print("breath wave:", breathWave)
                elif data[0] == 0x01:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            breathInfo = ord(data) 
                            # print("breathInfo:", breathInfo)
                            if(breathInfo == 1):
                                infoBreath = "Normal breath"
                                print("\tNormal breath")
                            elif(breathInfo == 2):
                                infoBreath = "Rapid breath"
                                print("\tRapid breath")
                            elif(breathInfo == 3):
                                infoBreath = "Slow breath"
                                print("\tSlow breath")

            elif data[0] == 0x80:#human presence data
                data = ser.read(1)
                if data[0] == 0x01:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            humanExist = ord(data) 
                            # print("humanExist:", humanExist)
                            print("humanExist:")
                            if(humanExist == 0):
                                print("\tUnoccupied")
                            elif(humanExist == 1):
                                print("\tOccupied")
                elif data[0] == 0x02:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            humanMove = ord(data) 
                            # print("humanMove:", humanMove)
                            print("humanMovement:")
                            if(humanMove == 0):
                                print("\tNone")
                            elif(humanMove == 1):
                                print("\tStationary")
                            elif(humanMove == 2):
                                print("\tActive")
                elif data[0] == 0x03:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            bodyMove = ord(data) 
                            # print("bodyMove:", bodyMove)
                elif data[0] == 0x04:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x02:
                            humanDist = []
                            for _ in range(2):
                                data = ser.read(1)
                                humanDist.append(data[0])
                            # print("humanDist:", humanDist)
                            distHuman = (humanDist[0] << 8 | humanDist[1])
                            print("\tdistance(cm):", distHuman)
                elif data[0] == 0x05:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x06:
                            humanPost = []
                            for _ in range(6):
                                data = ser.read(1)
                                humanPost.append(data[0])
                            # print("humanPost:", humanPost)
                            posX = ((humanPost[0] << 8 | humanPost[1]) & 0x7FFF)
                            if ((humanPost[0] << 8 | humanPost[1]) & 0x8000):
                                posX = -posX
                            print("\tPostX:", posX)
                            posY = ((humanPost[2] << 8 | humanPost[3]) & 0x7FFF)
                            if ((humanPost[2] << 8 | humanPost[3]) & 0x8000):
                                posY = -posY
                            print("\tPostY:", posY)
                            posZ = ((humanPost[4] << 8 | humanPost[5]) & 0x7FFF)
                            if ((humanPost[4] << 8 | humanPost[5]) & 0x8000):
                                posZ = -posZ
                            print("\tPostZ:", posZ)
            
            elif data[0] == 0x84:#sleep monitoring data
                data = ser.read(1)
                if data[0] == 0x01:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            bedState = ord(data) 
                            # print("humanExist:", humanExist)
                            print("bedState:")
                            if(bedState == 0):
                                print("\tBed out")
                            elif(bedState == 1):
                                print("\tBed in")
                elif data[0] == 0x02:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            stateSleep = ord(data) 
                            # print("humanMove:", humanMove)
                            print("stateSleep:")
                            if(stateSleep == 0):
                                print("\tDeep")
                            elif(stateSleep == 1):
                                print("\tLight")
                            elif(stateSleep == 2):
                                print("\tAwake")
                elif data[0] == 0x03:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x02:
                            timeSoberSleep = []
                            for _ in range(2):
                                data = ser.read(1)
                                timeSoberSleep.append(data[0])
                            # print("humanDist:", humanDist)
                            awakeTime = (timeSoberSleep[0] << 8 | timeSoberSleep[1])
                            print("\tawakeTime(mnt):", awakeTime)
                elif data[0] == 0x04:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x02:
                            timeLightSleep = []
                            for _ in range(2):
                                data = ser.read(1)
                                timeLightSleep.append(data[0])
                            # print("humanDist:", humanDist)
                            lightTime = (timeLightSleep[0] << 8 | timeLightSleep[1])
                            print("\tlightTime(mnt):", lightTime)
                elif data[0] == 0x05:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x02:
                            timeDeepSleep = []
                            for _ in range(2):
                                data = ser.read(1)
                                timeDeepSleep.append(data[0])
                            # print("humanDist:", humanDist)
                            deepTime = (timeDeepSleep[0] << 8 | timeDeepSleep[1])
                            print("\tdeepTime(mnt):", deepTime)
                elif data[0] == 0x06:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            sleepScore = ord(data) 
                            print("sleepScore(mnt):", sleepScore)
                elif data[0] == 0x0C:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x08:
                            sleepState = []
                            for _ in range(8):
                                data = ser.read(1)
                                sleepState.append(data[0])
                            print("\thumanExist:", sleepState[0])
                            print("\tsleepState:", sleepState[1])
                            print("\taverageBreath:", sleepState[2])
                            print("\taverageHearthrate:", sleepState[3])
                            print("\tnumOfTurning:", sleepState[4])
                            print("\tPercentOfSigBody:", sleepState[5])
                            print("\tPercentOfSmallBody:", sleepState[6])
                            print("\tnumOfRespiratoryPause:", sleepState[7])
                elif data[0] == 0x0D:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x0C:
                            sleepAnalys = []
                            for _ in range(12):
                                data = ser.read(1)
                                sleepAnalys.append(data[0])
                            print("\tsleepQualityScore:", sleepAnalys[0])
                            print("\ttotalHourSleep:", sleepAnalys[1])
                            print("\ttotalHourSleep:", sleepAnalys[2])
                            print("\tpercentWakingHour:", sleepAnalys[3])
                            print("\tpercentLightSleep:", sleepAnalys[4])
                            print("\tpercentDeepSleep:", sleepAnalys[5])
                            print("\tlengthTimeOutBed:", sleepAnalys[6])
                            print("\tnumTimeOutBed:", sleepAnalys[7])
                            print("\tnumTimeTurnBed:", sleepAnalys[8])
                            print("\tavgBreathing:", sleepAnalys[9])
                            print("\tavgHeartRate:", sleepAnalys[10])
                            print("\tnumOfRespiratoryPause:", sleepAnalys[11])
                elif data[0] == 0x0E:
                    data = ser.read(1)
                    if data[0] == 0x00:
                        data = ser.read(1)
                        if data[0] == 0x01:
                            data = ser.read(1)
                            abnormalSleep = ord(data) 
                            print("abnormalSleep:", abnormalSleep)

    # calVal = readHeartRate(heartValue)
    # totalRate += calVal
    # numReadings += 1
    # # dataSend = 0
    # if(numReadings == calibDuration):
    #     avgRate = totalRate / numReadings
    #     calibrationFactor = refHeartRate / avgRate
    #     print("Calibration factor: {:.2f}" .format(calibrationFactor))
    #     print("After calibration: {:.2f}" .format(heartValue * calibrationFactor))
        
    #     numReadings = 0
    #     totalRate = 0.0
    #     # dataSend = 1

    # if(dataSend == 1):
    #     data = {
    #         "heartValue": heartValue,
    #         "heartWave": heartWave,
    #         "bearthValue": breathWave,
    #         "bearthWave": breathValue,
    #         "breathInfo": infoBreath
    #     }
    #     dataSend = 0
    # else:       
    #     data = {
    #         "heartValue": heartValue,
    #         "heartWave": heartWave,
    #         "bearthValue": breathWave,
    #         "bearthWave": breathValue,
    #         "breathInfo": infoBreath
    #     }
    
    # data = {
    #         "heartValue": round(heartValue * calibrationFactor, 2),
    #         "heartWave": heartWave,
    #         "bearthValue": breathWave,
    #         "bearthWave": breathValue,
    #         "breathInfo": infoBreath
    #     }
    

    # start_time = millis()
    # client.publish("testing/data", json.dumps(data))
    # elapsed_time = millis() - start_time
    # if elapsed_time < 1000:
    #     time.sleep((1000 - elapsed_time) / 1000)
                            
