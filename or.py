# Orange Assist - A Google Assistant Companion
# @author Lucky Mallari
#
#
import os
import datetime
import logging
from threading import Timer
from orangeassist import OrangeAssistant
from req import Req
from resp import Resp
from gevent.pywsgi import WSGIServer
from flask import Flask, send_from_directory, request, make_response
from functools import wraps
import json
from config import Config

app = Flask(__name__)
cfg = Config()
orange = OrangeAssistant(cfg)
ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'

def log_print(m):
    logging.debug(m)
    print(m)

def delete_file(f):
    f = "output/" + f
    if os.path.exists(f):
        try:
            os.remove(f)
            logging.debug("Deleted: " + f)
        except Exception as e:
            logging.error(e)
    else:
        logging.debug("File not found to delete: " + f)


def sanitize_json(d):
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            sanitize_json(value)
    return d

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

def main():

    orange.connect()

    if cfg.is_debug:
        debug_loop()
        return

    log_print("Ready!")
    http_server = WSGIServer((cfg.host, int(cfg.port)), app)
    http_server.serve_forever()


def debug_loop():
    print("DebugMode! Keep sending request. 'exit' to stop.")
    while True:
        print("[Orange-->]: ", end='')
        q = input()
        if q == "exit":
            break
        r = Req("")
        r.request = q
        r.language = 'en-US'
        t, h = answer(r)
        print("[<--Google]: " + t)


def answer(r):
    text_response, html_response = orange.assist(r)
    return text_response, html_response


def check_auth(username, password):
    return username == cfg.username and password == cfg.password


def deny():
    return 'Nice try', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if cfg.username is None or cfg.password is None:
            return f(*args, **kwargs)
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return deny()
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
def index():
    return "orange!", 200


@app.route('/output/<f>', methods=['GET'])
def o(f):
    try:
        with open('output/' + f) as the_file:
            resp = the_file.read()
            the_file.close()
            return resp, 200
    except:
        return "can't find " + f, 404


@app.route('/assist/ask', methods=['POST'])
@requires_auth
def create_task():
    r = Req(request.data.decode('utf-8'))
    t, h = answer(r)
    log_print("request: " + r.request)

    if r.output_html_file:
        log_print("Output to " + r.output_html_file)
        with open("output/" + r.output_html_file, 'wb+') as the_file:
            try:
                h += "<!-- " + str(datetime.datetime.now()) + " -->\n" + h.decode('utf-8').encode("utf-8")
                the_file.write(h)
                log_print("Written to " + {r.output_html_file})
                if cfg.delete_output_files_sec and cfg.delete_output_files_sec > 0:
                    delete_timer = Timer(
                        int(cfg.delete_output_files_sec), delete_file, (r.output_html_file,))
                    delete_timer.start()
            except Exception as e:
                logging.error(e)
            finally:
                the_file.close()

    if r.output_audio_file:
        to_delete_audio = "output/" + r.output_audio_file
        if cfg.delete_output_files_sec and cfg.delete_output_files_sec > 0:
            delete_timer = Timer(
                2.0, delete_file, (to_delete_audio,))
            delete_timer.start()

    if not r.is_return_html:
        h = ""
    r = Resp(status=None,
             request=r.request,
             text=t,
             html=h if type(h) is str else h.decode("utf-8"),
             uuid=r.uuid,
             output_html_file=("/output/" + r.output_html_file) if r.output_html_file else None,
             output_audio_file=("/output/" + r.output_audio_file) if r.output_audio_file else None,
             )
    
    resp = make_response(json.dumps(sanitize_json(r.__dict__), indent=4, sort_keys=True, ensure_ascii=True), 200)
    return resp


if __name__ == '__main__':
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(curr_dir)
    log_print("# orange assist v1 #")
    c = json.dumps(cfg,
                   sort_keys=True,
                   indent=4,
                   separators=(',', ': '),
                   default=lambda o: o.__dict__)
    log_print("Server OrangeAssist with config:\n" + c)
    main()
