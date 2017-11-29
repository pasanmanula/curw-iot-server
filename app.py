#!/usr/local/bin/python3

from flask import Flask

app = Flask(__name__)


@app.route('/weatherstation/updateweatherstation')
def update_weather_station():
    return "Success"


@app.route('/')
def index():
    return "Hello, World!"


if __name__ == '__main__':
    app.run(debug=True)
