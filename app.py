from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app, manage_session=False)

@app.route("/")
def home():
    return render_template("index.html")

codes = {}

def run_code(code):
    print(code)

@socketio.on("connect")
def connect():
    codes[request.sid] = ""

@socketio.on("change")
def change(data):
    codes[request.sid] = data
    print(data)
    run_code(codes[request.sid])

@socketio.on("disconnect")
def disconnect():
    del codes[request.sid]