import sys
import multiprocessing
import threading
import binarian

from traceback import print_exc
from flask import Flask, Response, render_template, request

from std_wrapper import *

DEFAULT_TIME_LIMIT = 7

app = Flask(__name__)
app.debug = True

@app.route("/")
def home():
    return render_template("index.html")

def is_alive(process: multiprocessing.Process):
    try:
        return process.is_alive()
    except ValueError:
        return False

def time_limiter(proc : multiprocessing.Process, pipe):
    try:
        if not proc.is_alive(): return
    except ValueError: return
    proc.terminate()
    pipe.send(f"Your program was running over {DEFAULT_TIME_LIMIT} seconds.\n"
                "You can run this program using binarian locally installed on your pc.")

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

def run_code(code):

    pipe_rec, pipe_sen = multiprocessing.Pipe(False)

    interp = multiprocessing.Process(target=run_inter, args=(code, pipe_sen))
    limiter = threading.Timer(DEFAULT_TIME_LIMIT, time_limiter, (interp, pipe_sen))

    interp.start()
    limiter.start()

    while True:
        try:
            if interp.is_alive():
                interp.close()
                break
        except ValueError: break
    rec = pipe_rec.recv()
    return rec
            

@app.route("/execute", methods=["POST"])
def execute():
    return Response(run_code(request.get_data(as_text=True)))