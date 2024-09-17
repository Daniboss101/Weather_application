import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})

# Setup logging
handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

from weather_module import weather_blueprint
from forecast_module import forecast_blueprint

# Register weather blueprint
app.register_blueprint(weather_blueprint)
app.register_blueprint(forecast_blueprint)
@app.route('/')
def index():
    app.logger.info('Processing default request')
    return "hello world"


if __name__ == '__main__':
    app.run(debug=True, port=5000)
