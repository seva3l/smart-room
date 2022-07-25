from flask import Flask
from app.database.db import initialize_db, db
from config import app_config, Config
from dotenv import load_dotenv
from flask_login import LoginManager
import os
from flask_apscheduler import APScheduler
load_dotenv()

app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
# app.config.from_object(app_config['development'])
app.config.from_object(Config())
initialize_db(app)
scheduler = APScheduler()
scheduler.init_app(app)





from app.route.routes import save_data
scheduler.add_job(id='Scheduled Task',func=save_data,trigger='interval',minutes=30)

from app.route import routes

