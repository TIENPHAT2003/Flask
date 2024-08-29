from app import app, socketio, Thread, run_mqtt

app.app_context().push()
if __name__ == "__main__":
    mqtt_thread = Thread(target=run_mqtt)
    mqtt_thread.start()
    # socketio.run(app,host="0.0.0.0", port=5050, use_reloader=True, debug=True)
    app.run(host='0.0.0.0', port=5050, debug=True)