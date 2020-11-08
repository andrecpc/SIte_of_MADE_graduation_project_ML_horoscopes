# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
import pandas as pd
import json
import logging
from datetime import date, timedelta
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

PREDICTIONS_DF = pd.read_csv("horoscopes.csv", sep=";", index_col="date")
USER_DICT = {}

app = Flask(__name__)
app.debug = True

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}
 
def get_prediction_from_model(target_date, target_sign): #Not implemented
  return("""Это благоприятный день для общения с теми, кто дорог вам и близок по духу. 
  			Отношения, которые в последнее время складывались напряженно, 
  			сейчас меняются к лучшему, потому что многие готовы к компромиссам, 
  			стараются сглаживать острые углы и хотят достичь взаимопонимания, 
  			а не только доказать свою правоту.Хочется отложить дела на потом, 
  			отдохнуть. Но важно не забывать об обещаниях, данных раньше. 
  			Постарайтесь сделать все, что запланировали. 
  			Скорее всего, у вас останется достаточно времени и для того, 
  			чтобы немного развлечься, восстановить силы.""")

def get_prediction(target_date, target_sign, PREDICTIONS_DF):
  if target_date in PREDICTIONS_DF.index:
    return(PREDICTIONS_DF.loc[target_date,target_sign])
  else:
    return(get_prediction_from_model(target_date, target_sign))
  

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
		today_date = date.today()
		USER_DICT[request.json['session']['user_id']] = request.json['request']['command']
		text = "Гороскоп на сегодня. \n"+get_prediction(str(today_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
		buttons = [{"title":"На завтра"}, {"title":"На другую дату"}]

	elif request.json['request']['command'] == 'на завтра':
		tomorrow_date = date.today() + timedelta(days=1)
		text = "Гороскоп на завтра. \n"+get_prediction(str(tomorrow_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
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