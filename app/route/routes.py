from glob import glob
import re
from app import app
from flask import render_template, request, Response, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user, current_user
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
    temp = '24' if setting[0] == 'None' else str(setting[0])
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
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
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
    indoor_temp_data = Sensor.query.filter(Sensor.name == 'Indoor Temperature Sensor')
    outdoor_temp_data = Sensor.query.filter(Sensor.name == 'Outdoor Temperature Sensor')
    indoor_humi_data = Sensor.query.filter(Sensor.name == 'Indoor Humidity Sensor')
    outdoor_humi_data = Sensor.query.filter(Sensor.name == 'Outdoor Humidity Sensor')
    pm1_data = Sensor.query.filter(Sensor.name == 'PM1 Dust Sensor')
    pm2_data = Sensor.query.filter(Sensor.name == 'PM2.5 Dust Sensor')
    carbon_data = Sensor.query.filter(Sensor.name == 'Carbon Dioxide Sensor')

    # temperature 
    temperature_label = [row.created_at.strftime("%m/%d/%Y, %H:%M:%S") for row in indoor_temp_data]
    indoor_temp_value = [row.value for row in indoor_temp_data]
    outdoor_temp_value = [row.value for row in outdoor_temp_data]
    # humidity
    humidity_label = [row.created_at.strftime("%m/%d/%Y, %H:%M:%S") for row in indoor_humi_data]
    indoor_humi_value = [row.value for row in indoor_humi_data]
    outdoor_humi_value = [row.value for row in outdoor_humi_data]
    #dust
    dust_label = [row.created_at.strftime("%m/%d/%Y, %H:%M:%S") for row in pm1_data]
    pm1_value = [row.value for row in pm1_data]
    pm2_value = [row.value for row in pm2_data]
    
    # co2 
    co2_label = [row.created_at.strftime("%m/%d/%Y, %H:%M:%S") for row in carbon_data]
    carbon_value = [row.value for row in carbon_data]
   
    file = open("settings.txt", "r")
    setting = file.readlines()
    file.close()
    temp = 24 if setting[0] == 'None' else float(setting[0])
    form = TemperatureForm()
    page = request.args.get('page', 1, type=int)
    pagination = Sensor.query.order_by(Sensor.created_at.desc()).paginate(page, per_page=7)
    next_url = url_for('admin', page=pagination.next_num) if pagination.has_next else None
    prev_url = url_for('admin', page=pagination.prev_num) if pagination.has_prev else None
    if request.method == 'POST':
        
        with open('settings.txt', 'w') as f:
            f.write(str(form.temperature.data))
            f.close()
            temp = form.temperature.data

    template_data = {
        "form": form,
        "temp": temp,
        "pagination": pagination,
        "next_url": next_url,
        "prev_url": prev_url,
        "temp_labels": temperature_label,
        "indoor_temp": indoor_temp_value,
        "outdoor_temp": outdoor_temp_value,
        "humi_labels": humidity_label,
        "indoor_humi": indoor_humi_value,
        "outdoor_humi": outdoor_humi_value,
        "dust_labels": dust_label,
        "pm1": pm1_value,
        "pm2": pm2_value,
        "co2_labels": co2_label,
        "carbon_dioxide": carbon_value   
    }
    return render_template("admin.html", **template_data)

@app.get('/tables')
def view_table():
   

    datas = sensor.fetch_data()
    return render_template("tables.html", datas = datas)

@app.get('/download')
def download():
    datas = Sensor.query.all()
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
        sh.write(idx+1, 0 , str(data.id))
        sh.write(idx+1, 1 , str(data.name))
        sh.write(idx+1, 2 , str(data.description))
        sh.write(idx+1, 3 , str(data.value))
        sh.write(idx+1, 4 , str(data.created_at))
        idx += 1

    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=sensors_data_report.xls"})