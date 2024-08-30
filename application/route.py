from application import app, socketio
from application import db
from application.form import ConfigForm, DeviceForm
from application.model import DeviceConfig, MQTTConfig, MQTTData
from flask import render_template, request, url_for, redirect,flash,get_flashed_messages, jsonify,copy_current_request_context
import json
import random
from application.SICK import SICK_SENSOR
from paho.mqtt import client as mqtt_client
from flask_socketio import SocketIO, emit, disconnect

app.app_context().push()
sensor = SICK_SENSOR()
# broker = 'vm01.i-soft.com.vn'
# port = 1883
client_id = f'subscribe-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    with app.app_context():
        config = MQTTConfig.query.filter_by(id=1).first()
        broker = config.broker
        port = config.port
        usr = config.usr
        pwd = config.pwd
        
    client = mqtt_client.Client()
    client.username_pw_set(usr, pwd)
    client.on_connect = on_connect
    client.connect(broker, int(port))

    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        subscribe(client)
    else:
        print("Failed to connect, return code %d\n", rc)

def find_sensor_by_topic(topic):
    try:
        config = DeviceConfig.query.filter_by(topic=topic).first()
        return config.sensor if config else None
    except Exception as e:
        # Handle any exceptions that may occur during the query
        print(f"Error occurred while querying: {e}")
        return None

def find_type_by_topic(topic):
    try:
        config = DeviceConfig.query.filter_by(topic=topic).first()
        return config.type if config else None
    except Exception as e:
        # Handle any exceptions that may occur during the query
        print(f"Error occurred while querying: {e}")
        return None

def get_all_topics():
    try:
        all_configs = DeviceConfig.query.all()
        results = [config.topic for config in all_configs]
        return results
    except Exception as e:
        # Handle any exceptions that may occur during the query
        print(f"Error occurred while fetching topics: {e}")
        return []

def subscribe(client: mqtt_client):  
    def on_message(client, userdata, msg):
        data = ""
        decoded_payload = msg.payload.decode()
        with app.app_context():
            sensorN = find_sensor_by_topic(msg.topic)
            type = find_type_by_topic(msg.topic)
        match sensorN:
            case "MPB10":
                value = sensor.get_mpb10_value(decoded_payload)
                data = {
                    type: sensorN,
                    "value": value
                }
            case "OD2000":
                value = sensor.get_od2000_value(decoded_payload)
                data = {
                    type: sensorN,
                    "value": value
                }
            case "WTM10L":
                value = sensor.get_wtm10l_value(decoded_payload)
                data = {
                    type: sensorN,
                    "value": value
                }
            case "CSS":
                value = sensor.get_css_value(decoded_payload)
                data = {
                    type: sensorN,
                    "value": value
                }  
            case "PBS":
                value = sensor.get_pbs_value(decoded_payload)
                data = {
                    type: sensorN,
                    "value": value
                }                            
            case _:
                print("Not supported yet")
        with app.app_context():
            # print(data)
            # Convert the list to a JSON string
            dbdata = MQTTData(sensor=sensorN, data=json.dumps(data))
            db.session.add(dbdata)
            db.session.commit()
        socketio.emit('mqtt_message', data)

    with app.app_context():
        topics = get_all_topics()
    for topic in topics:
        # print(topic)
        client.subscribe(topic)
    client.on_message = on_message
    
def run_mqtt():
    client = connect_mqtt()
    client.loop_start()
    subscribe(client) 

@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    run_mqtt()
    return render_template("index.html")  

@app.route('/mqtt/config', methods=['POST', 'GET'])
def mqtt_config():
    deviceForm = DeviceForm()
    configForm = ConfigForm()
    if deviceForm.validate_on_submit():
        dconf = DeviceConfig.query.filter_by(topic=deviceForm.topic.data).first()
        if dconf is None:
            dconf = DeviceConfig(
                topic=deviceForm.topic.data, 
                sensor=deviceForm.sensor.data, 
                type=deviceForm.type.data
            )
            try:
                db.session.add(dconf)
                db.session.commit()
                flash("Device added successfully")
            except Exception as e:
                db.session.rollback()  # Rollback on error
                print(f"Error adding device: {e}")
                flash("Failed to add device")
        subscribe(mqtt_client.Client())
    if configForm.validate_on_submit():
        broker = configForm.broker.data
        port = configForm.port.data
        usr = configForm.usr.data
        pwd = configForm.pwd.data

        print("MQTT broker:", broker)
        print("MQTT port:", port)
        print("MQTT user:", usr)
        print("MQTT pass:", pwd)

        try:
            with app.app_context():
                MQTTConfig.query.filter_by(id=1).update({
                    MQTTConfig.broker:broker,
                    MQTTConfig.port:port,
                    MQTTConfig.usr:usr,
                    MQTTConfig.pwd:pwd,
                    }, synchronize_session=False)
                db.session.commit()
                flash("MQTT configuration updated successfully")
        except Exception as e:
            db.session.rollback()  # Rollback on error
            print(f"Error updating MQTT config: {e}")
            flash("Failed to update MQTT configuration")
    dev_conf = DeviceConfig.query.order_by(DeviceConfig.date_added)
    return render_template('mqttconfig.html',
                           deviceForm=deviceForm,
                           configForm=configForm,
                           dev_conf=dev_conf)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500