import json
import time

from bottle import Bottle, request

from FeatureCloud.app.engine.app import app

api_server = Bottle()


# CAREFUL: Do NOT perform any computation-related tasks inside these methods, nor inside functions called from them!
# Otherwise your app does not respond to calls made by the FeatureCloud system quickly enough
# Use the threaded loop in the app_flow function inside the file logic.py instead


@api_server.post('/setup')
def ctrl_setup():
    time.sleep(1)
    print(f'[CTRL] POST /setup')
    payload = request.json
    app.handle_setup(payload.get('id'), payload.get('coordinator'), payload.get('clients'))
    return ''


@api_server.get('/status')
def ctrl_status():
    print(f'[CTRL] GET /status')
    return app.handle_status()


@api_server.route('/data', method='GET')
def ctrl_data_out():
    print(f'[CTRL] GET /data')
    return app.handle_outgoing()


@api_server.route('/data', method='POST')
def ctrl_data_in():
    print(f'[CTRL] POST /data')
    app.handle_incoming(request.body.read(), request.query['client'])
    return ''
