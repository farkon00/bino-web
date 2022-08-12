import sys
from traceback import print_exc
import binarian

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room

from std_wrapper import *

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app, manage_session=False)

@app.route("/")
def home():
    return render_template("index.html")

codes = {}

def run_code(code, sid):
    out = OutputWrapper()
    sys.stdout = out
    sys.stderr = out
    sys.stdin = StdinWrapper()
    try:
        binarian.main(program=code)
    except Exception:
        print("While running your program an exception occured:", file=sys.stdout)
        print_exc()
    except BaseException:
        pass
    emit("reset_out", to=sid)
    emit("add_out", out.output, to=sid)

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