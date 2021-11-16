from bottle import Bottle

from engine.app import app

web_server = Bottle()


# CAREFUL: Do NOT perform any computation-related tasks inside these methods, nor inside functions called from them!
# Otherwise your app does not respond to calls made by the FeatureCloud system quickly enough
# Use the threaded loop in the app_flow function inside the file logic.py instead


@web_server.route('/')
def index():
    print(f'[WEB] GET /')
    return f'State: {app.current_state.name}'
