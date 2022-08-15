import sys
import multiprocessing
import threading
import binarian

from traceback import print_exc
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, close_room

from std_wrapper import *

DEFAULT_TIME_LIMIT = 7

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app, manage_session=False)

@app.route("/")
def home():
    return render_template("index.html")

codes = {}

def time_limiter(sid, proc : multiprocessing.Process, emit_queue):
    if proc.is_alive():
        proc.kill()
        while proc.is_alive():
            pass
        proc.close()
        emit_queue.append(("reset_out", sid))
        emit_queue.append(("add_out", f"Your program was running over {DEFAULT_TIME_LIMIT} seconds.\nYou can run this program using binarian locally installed on your pc.", sid))

def run_inter(sid, code, emit_queue):
    out = OutputWrapper()
    sys.stdout = out
    sys.stderr = out
    sys.stdin = StdinWrapper()
    try:
        binarian.main(program=code)
    except Exception:
        print("While running your program an exception occured: ")
        print_exc()
    except BaseException:
        pass
    emit_queue.append(("reset_out", sid))
    emit_queue.append(("add_out", out.output, sid))

def run_code(code, sid):
    emit_queue = []

    interp = multiprocessing.Process(target=run_inter, args=(sid, code, emit_queue))
    limiter = threading.Timer(DEFAULT_TIME_LIMIT, time_limiter, (sid, interp, emit_queue))

    interp.start()
    limiter.start()

    while True:
        if emit_queue:
            emit_request = emit_queue.pop(0)
            emit(*emit_request[:-1], to=emit_request[-1])

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