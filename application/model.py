from application.route import db
from datetime import datetime

class DeviceConfig(db.Model):
    __tablename__ = 'device_config'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    sensor = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

def __init__(self, id, topic, sensor, type, date_added):
   self.id = id
   self.topic = topic
   self.sensor = sensor
   self.type = type
   self.date_added = date_added

class MQTTConfig(db.Model):
    __tablename__ = 'mqtt_config'
    id = db.Column(db.Integer, primary_key=True)
    broker = db.Column(db.String(200), nullable=False)
    port = db.Column(db.String(200), nullable=False)
    usr = db.Column(db.String(200), nullable=True)
    pwd = db.Column(db.String(200), nullable=True)
    
def __init__(self, id, broker, port, usr, pwd):
   self.id = id
   self.broker = broker
   self.port = port
   self.usr = usr
   self.pwd = pwd
    
class MQTTData(db.Model):
    __tablename__ = 'mqtt_data'
    id = db.Column(db.Integer, primary_key=True)
    sensor = db.Column(db.String(200), nullable=False)
    data = db.Column(db.String(200), nullable=False)
    
def __init__(self, id, sensor, data):
   self.id = id
   self.sensor = sensor
   self.data = data
