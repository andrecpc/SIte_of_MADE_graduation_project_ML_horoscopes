# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import pandas as pd
import json
import logging
from datetime import date
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
application = Flask(__name__)

SIGNS = ["овен",
	"телец",
	"близнецы",
	"рак",
	"лев",
	"дева",
	"весы",
	"скорпион",
	"козерог",
	"стрелец",
	"водолей",
	"рыбы",
]

PREDICTIONS_DF = pd.read_csv("horoscopes.csv", sep=";")

app = Flask(__name__)
app.debug = True

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}

# def get_prediction(target_date, target_sign):
# 	if target_date in PREDICTIONS_DF['date'].values

@app.route("/")
def hello():
	return "Welcome to my page"

@app.route('/index')
def index():
	return'<h1>Heroku Deploy</h1>'

@app.route("/marusya", methods=['POST', 'GET'])
def marusya():
	return "Marusya"

@app.route("/marussia", methods=['POST'])
def main():
	logging.info("Request: %r", request.json)
	card = {}
	buttons = []

	if request.json['session']['new']:
		text = "Привет! Это навык Эй Ай Гороскоп. Какой у Вас знак зодиака?"

	elif request.json['request']['command'] in SIGNS:
		user_sign = request.json['request']['command']
		text = "Гороскоп на сегодня. \n"+PREDICTIONS_DF.loc[0, user_sign]
		buttons = [{"title":"На завтра"}, {"title":"На другую дату"}]

	elif request.json['request']['command'] == 'на завтра':
		text = "Гороскоп на завтра. \n"+PREDICTIONS_DF.loc[0, user_sign]
		buttons = [{"title":"На сегодня"}, {"title":"На другую дату"}]

	elif request.json['request']['command'] == 'на другую дату':
		text = 'На какую дату?'

	elif request.json['request']['command'] == 'on_interrupt':
		text = 'Пока!'

	else:
		text = request.json['request']['command']
	response = {
		"version":request.json['version'],
		'session':request.json['session'],
		"response": {
			"end_session": False,
			"text" : text,
			"card" : card, 
			"buttons" : buttons 
		}

	}
	logging.info("response %r", response)

	return json.dumps (response, ensure_ascii=False, indent=2)


@app.route("/debug", methods=['POST'])
def debug():
	response = {
	"version":request.json['version'],
	'session':request.json['session'],
	"response": {
		"end_session": False,
		"text" : "hi"
	}}
	return response


if __name__ == '__main__':
	app.run(debug=True)