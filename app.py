from flask import Flask, send_from_directory, make_response
from flask_limiter import Limiter
import subprocess
import os

app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('www', 'index.html')


def run(cmd):
    result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == os.EX_OK:
        print('stdout', repr(result.stdout))
        return result.stdout or '<meta http-equiv="refresh" content="1;url=/">\nok', 200
    else:
        return result.stderr.decode('utf-8') or 'error', 500


limiter = Limiter(app, key_func=lambda: 1) # limiter for all users, NOTE: only for one worker


@app.route('/reset', methods=['POST'])
@limiter.limit("1 per 10 seconds")
def reset():
    return run('sudo systemctl restart clover-cloud')


@app.route('/stop', methods=['POST'])
@limiter.limit("1 per 10 seconds")
def stop():
    return run('sudo systemctl stop clover-cloud')


@app.route('/restart', methods=['POST'])
def restart():
    return 'not implemented', 501


@app.route('/status')
def status():
    result = subprocess.run('systemctl is-active clover-cloud'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stderr or result.stdout


@app.route('/log')
def log():
    resp = make_response(subprocess.check_output('sudo journalctl _SYSTEMD_INVOCATION_ID=$(systemctl show -p InvocationID --value clover-cloud.service) -o cat --no-pager', shell=True))
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return resp
