from flask import Flask, render_template, flash, request, url_for, redirect
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, emit, send
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random
from SICK import SICK_SENSOR
from paho.mqtt import client as mqtt_client
from threading import Thread

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = "namdhayplayground"
db = SQLAlchemy(app)
socketio = SocketIO(app)

broker = 'vm01.i-soft.com.vn'
port = 1883
MQTT_TOPICS_SUBSCRIBE = ["isoft/node 12/sick1", "isoft/node 12/sick2"]
client_id = f'subscribe-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        subscribe(client)
    else:
        print("Failed to connect, return code %d\n", rc)
 
sensor = SICK_SENSOR()
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        decoded_payload = msg.payload.decode()
        valuempb10 = sensor.get_mpb10_value(decoded_payload)
        print(valuempb10)
        data ={
            "Gyro": "MPB10",
            "value": valuempb10
        }
        socketio.emit('mqtt_message',  data)
        jsonod2000 = '{"iolink":{"valid":true,"time":1723049390,"value":[252,35,116,55,247,3]},"iqValue":false}'
        valueod2000 = sensor.get_od2000_value(jsonod2000)
        data1 ={
            "Distance": "OD2000",
            "value": valueod2000
        }
        socketio.emit('mqtt_message',  data1)
        jsonwtm10l = '{"iolink":{"valid":true,"time":1723049390,"value":[0,183,0,122]},"iqValue":false}'
        valuewtm10l = sensor.get_wtm10l_value(jsonwtm10l)
        data2 ={
            "Distance": "WTM10L",
            "value": valuewtm10l
        }
        socketio.emit('mqtt_message',  data2)
        jsoncss = '{"iolink":{"valid":true,"time":1723049390,"value":[0,0,0,0,0,0,1,201,0,0,0,0]},"iqValue":false}'
        valuecss = sensor.get_css_value(jsoncss)
        data3 ={
            "Color": "CSS",
            "value": valuecss
        }
        socketio.emit('mqtt_message',  data3)

        jsonpbs = '{"iolink":{"valid":true,"time":1723049390,"value":[63,128,193,252,0]},"iqValue":false}'
        valuepbs = sensor.get_pbs_value(jsonpbs)
        data4 ={
            "Pressure": "PBS",
            "value": valuepbs
        }
        socketio.emit('mqtt_message',  data4)
    for topic in MQTT_TOPICS_SUBSCRIBE:
        client.subscribe(topic)
    client.on_message = on_message
def OD2000():
    valueod2000 = sensor.get_od2000_value()
    
def run_mqtt():
    client = connect_mqtt()
    client.loop_start()
    subscribe(client)

@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("index.html")  

class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<Topic: %r>' % self.topic
    class ConfigForm(FlaskForm):
        topic = StringField("Topic: ", validators=[DataRequired()])
        submit = SubmitField("Subscribe")

@app.route('/mqtt/config', methods=['POST', 'GET'])
def mqtt_config():
    form = Config.ConfigForm()
    if form.validate_on_submit():
        conf = Config.query.filter_by(topic=form.topic.data).first()
        if conf is None:
            conf = Config(topic=form.topic.data)
            db.session.add(conf)
            db.session.commit()
        flash("Add successfully")   
    mqtt_conf = Config.query.order_by(Config.date_added)  

    return render_template('mqttconfig.html',
                           form=form,
                           mqtt_conf=mqtt_conf)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@socketio.on('connect')
def handle_connect():
    client_ip = request.remote_addr
    print(f'Client connected with IP: {client_ip}')
@socketio.on('message')
def handle_message(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)
    
@socketio.on('custom_event')
def handle_custom_event(data):
    emit('custom_response', data, broadcast=True)
    print(f'Received data: {data}')
        
    
