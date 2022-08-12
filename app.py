from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app, manage_session=False)

@app.route("/")
def home():
    return render_template("index.html")

codes = {}

def run_code(code, sid):
    emit("reset_out", to=sid)
    emit("add_out", "Hi from server\n" + code, to=sid)

@socketio.on("connect")
def connect():
    codes[request.sid] = ""
    join_room(request.sid)

@socketio.on("change")
def change(data):
    codes[request.sid] = data
    run_code(codes[request.sid], request.sid)

@socketio.on("disconnect")
def disconnect():
    close_room(request.sid)
    del codes[request.sid]