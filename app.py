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

def time_limiter(sid, proc : multiprocessing.Process, pipe):
    if proc.is_alive():
        proc.kill()
        while proc.is_alive():
            pass
        proc.close()

        pipe.send(f"Your program was running over {DEFAULT_TIME_LIMIT} seconds.\nYou can run this program using binarian locally installed on your pc.")

def run_inter(code, pipe):
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
    pipe.send(out.output)

def run_code(code, sid):
    emit_queue = []

    pipe_rec, pipe_sen = multiprocessing.Pipe(False)

    interp = multiprocessing.Process(target=run_inter, args=(code, pipe_sen))
    limiter = threading.Timer(DEFAULT_TIME_LIMIT, time_limiter, (sid, interp, pipe_sen))

    interp.start()
    limiter.start()

    while True:
        if emit_queue:
            emit_request = emit_queue.pop(0)
            emit(*emit_request[:-1], to=emit_request[-1])
        try:
            is_alive = interp.is_alive()
        except ValueError:
            is_alive = False
        if not is_alive:
            rec = pipe_rec.recv()
            emit("reset_out", to=sid)
            emit("add_out", rec, to=sid)
            break

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