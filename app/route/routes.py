from glob import glob
import re
from app import app
from flask import render_template, request, Response, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user
from wtforms import StringField, PasswordField, FloatField
from wtforms.validators import  DataRequired
import io 
import time
import serial
import json
import xlwt
from app.models import User, Sensor
from app.database.db import db



##############VARIABALES#####################
indoor_temperature = 30
indoor_humidity =  35
outdoor_temperature = 27
outdoor_humidity =  86
carbon_dioxide = 162
pm1 = 0.6
pm2 = 0.5
electric_fan = "ON"
aircon = "OFF"
sensor_length = 8
#############################################
from app.controllers import SensorControler
sensor = SensorControler()
def save_data():
    
    print("saving data sensors data from arduino>>>>>>>>>>>>>>>>>")
    with app.app_context():
        if sensor_length == 8:
            sensor1 = Sensor(name="Indoor Temperature Sensor", description="DHT22 Sensor", value=indoor_temperature)
            db.session.add(sensor1)

            sensor2 = Sensor(name="Outdoor Temperature Sensor",description="DHT22 Sensor",value=outdoor_temperature)
            db.session.add(sensor2)

            sensor3 = Sensor(name="Indoor Humidity Sensor",description="DHT22 Sensor",value=indoor_humidity)
            db.session.add(sensor3)

            sensor4 = Sensor(name="Outdoor Humidity Sensor",description="DHT22 Sensor",value=outdoor_humidity)
            db.session.add(sensor4)

            sensor5 = Sensor(name="PM1 Dust Sensor",description="DSM501A Sensor",value=pm1)
            db.session.add(sensor5)

            sensor6 = Sensor(name="PM2.5 Dust Sensor",description="DHT22 Sensor",value=pm2)
            db.session.add(sensor6)

            sensor7 = Sensor(name="Carbon Dioxide Sensor",description="MQ135 Gas Sensor",value=carbon_dioxide)
            db.session.add(sensor7) 

            db.session.commit()

def get_values_from_serial():
    print("Reading data from arduino>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    file = open("settings.txt", "r")
    setting = file.readlines()
    file.close()
    temp = float(setting[0])
    global indoor_temperature
    global indoor_humidity
    global outdoor_temperature
    global outdoor_humidity
    global pm1
    global pm2
    global carbon_dioxide
    global sensor_length
    ser = serial.Serial("/dev/ttyACM0",9600, timeout = 1)
    while True:
        ser.write(temp.encode('utf-8'))
        try:
             if ser.inWaiting() > 0:
                read_serial = str(ser.readline())
                data_list = read_serial.split("|")
                print(len(data_list))
                if len(data_list) == 8:
                    sensor_length = 8
                    indoor_temperature = float(data_list[1])
                    indoor_humidity = float(data_list[2])
                    outdoor_temperature = float(data_list[3])
                    outdoor_humidity = float(data_list[4])
                    pm1 = float(data_list[5])
                    pm2 = float(data_list[6])
                    carbon_dioxide = data_list[7]
        except json.decoder.JSONDecodeError:
            pass
        except serial.serialutil.SerialException:
            pass
        time.sleep(3)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Placeholder labels to enable form rendering
    # username = StringField(validators=[Optional()])

class TemperatureForm(FlaskForm):
    temperature = FloatField('Username', validators=[DataRequired()])


@app.route('/', methods=('GET', 'POST'))
def index():
    sensor.create()
    data = {
        "indoor_temperature": str(indoor_temperature),
        "indoor_humidity": str(indoor_humidity),
        "outdoor_temperature": str(outdoor_temperature),
        "outdoor_humidity": str(outdoor_humidity),
        "carbon_dioxide": str(carbon_dioxide),
        "pm1": str(pm1),
        "pm2": str(pm2),
        "electric_fan": electric_fan,
        "aircon": aircon
    }
    # sensor.create()
    return render_template("index.html", **data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == "POST":
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user.check_password(password):
                    login_user(user)
                    return redirect(url_for('admin'))
            else:
                print("Invalid Username or password!", "danger")
    return render_template("login.html", form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    file = open("settings.txt", "r")
    setting = file.readlines()
    file.close()
    temp = float(setting[0])
    form = TemperatureForm()
    if request.method == 'POST':
        
        with open('settings.txt', 'w') as f:
            f.write(str(form.temperature.data))
            f.close()
            temp = form.temperature.data
    return render_template("admin.html", form = form,temp = temp)

@app.get('/tables')
def view_table():
   

    datas = sensor.fetch_data()
    return render_template("tables.html", datas = datas)

@app.get('/download')
def download():
    datas = sensor.fetch_data()
    output = io.BytesIO()
    workbook = xlwt.Workbook()

    sh = workbook.add_sheet('Sensors Data')

    # add headers 
    sh.write(0, 0, 'ID')
    sh.write(0, 1, 'Name')
    sh.write(0, 2, 'Description')
    sh.write(0, 3, 'Value')
    sh.write(0, 4, 'CreatedAt')

    idx = 0
    for data in datas:
        print(data)
        sh.write(idx+1, 0 , str(data.id))
        sh.write(idx+1, 1 , str(data.name))
        sh.write(idx+1, 2 , str(data.description))
        sh.write(idx+1, 3 , str(data.value))
        sh.write(idx+1, 4 , str(data.created_at))
        idx += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=sensors_data_report.xlsx"})