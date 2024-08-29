# Error save error on server
#04092023
#  fix error, realtime update data to web
#  MCU disconnect after > 30 minutes
################################################################
from application import app
from application import socketio

app.app_context().push()
if __name__ == '__main__':
    print("hello world!")
    socketio.run(app,host="0.0.0.0", port=5050, use_reloader=False, debug=True)
    # app.run(debug = True, port=5003)