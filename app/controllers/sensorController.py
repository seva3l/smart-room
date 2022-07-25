from tracemalloc import Snapshot
from app.models import Sensor
from app.database.db import db 

class SensorControler():

    def fetch_data(self):
        data = Sensor.query.all()
        return data

    def create(self):
        data = Sensor(name="T2",description="Temperature Sensor",value=20)
        db.session.add(data)
        db.session.commit()

        return True