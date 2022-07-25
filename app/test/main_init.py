from flask import Flask, render_template
import serial
import threading
import json
import time
mutex = threading.Lock()
app = Flask(__name__)
indoor_temperature = 0
indoor_humidity = 0
outdoor_temperature = 0
outdoor_humidity = 0
air_quality = 0
last_temperature_value = 0
last_air_humidity_value = 0
@app.route('/')
def index():
    print("indez",indoor_humidity)
    data = {
        "indoor_temperature": str(indoor_temperature),
        "indoor_humidity": str(indoor_humidity),
        "outdoor_temperature": str(outdoor_temperature),
        "outdoor_humidity": str(outdoor_humidity),
    }
    return render_template("index.html",**data)
def get_values_from_serial():
    global indoor_temperature
    global indoor_humidity
    global outdoor_temperature
    global outdoor_humidity
    ser = serial.Serial("/dev/ttyACM0",9600, timeout = 1)
    while True:
        try:
             if ser.inWaiting() > 0:
                read_serial = str(ser.readline())
                data_list = read_serial.split("|")
                print(len(data_list))
                if len(data_list) == 4 or len(data_list) == 5:
                    temp = data_list[0].split("'")
                    indoor_temperature = temp[1]
                    indoor_humidity = data_list[1]
                    outdoor_temperature = data_list[2]
                    outdoor_humidity = data_list[3]
                    print(float(temp[1]))
                    print(float(data_list[1]))
                    print(float(data_list[2]))
                    print(float(data_list[3]))                     
        except json.decoder.JSONDecodeError:
            pass
        except serial.serialutil.SerialException:
            pass
        time.sleep(3)
dht22_thread = threading.Thread(target=get_values_from_serial)
if __name__ == '__main__':
    dht22_thread.start()
    app.run(host='0.0.0.0')