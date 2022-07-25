from app.database.db import db
from sqlalchemy.sql import func

class Sensor(db.Model):
    __tablename__ = "sensors"
    id  = db.Column(db.Integer, primary_key = True)
    name  = db.Column(db.String(60))
    description  = db.Column(db.String(60))
    value = db.Column(db.Float)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())