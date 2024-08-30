from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired

class DeviceForm(FlaskForm):
    topic = StringField("Topic: ", validators=[DataRequired()])
    sensor = StringField("Sensor: ", validators=[DataRequired()])
    type = StringField("Type: ", validators=[DataRequired()])
    submit = SubmitField("Subscribe")
    
class ConfigForm(FlaskForm):
    broker = StringField("Broker: ", validators=[DataRequired()])
    port = StringField("Port: ", validators=[DataRequired()])
    usr = StringField("Usr: ", validators=[])
    pwd = StringField("Pwd: ", validators=[])
    submit = SubmitField("Save")