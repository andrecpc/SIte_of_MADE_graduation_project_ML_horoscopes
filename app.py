# -*- coding: utf-8 -*-


from __future__ import unicode_literals
import json
import requests as req
import json
import logging
import numpy as np
import pandas as pd
from zodiac_sign import get_zodiac_sign
from astropy.time import Time
from astroquery.jplhorizons import Horizons

from datetime import datetime, date, timedelta
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request, render_template, request
application = Flask(__name__)
application.debug = True
model_url = "http://188.40.133.2:12121/custom_prediction"

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

SIGNS_DICT = {
  '0':"main_horo",
  '1':"овен",
  '2':"телец",
  '3':"близнецы",
  '4':"рак",
  '5':"лев",
  '6':"дева",
  '7':"весы",
  '8':"скорпион",
  '9':"козерог",
  '10':"стрелец",
  '11':"водолей",
  '12':"рыбы",
}

INV_SIGNS_DICT = {
  "main_horo":'0',
  "овен":'1',
  "телец":'2',
  "близнецы":'3',
  "рак":'4',
  "лев":'5',
  "дева":'6',
  "весы":'7',
  "скорпион":'8',
  "козерог":'9',
  "стрелец":'10',
  "водолей":'11',
  "рыбы":'12',
}

RU_EN_SIGNS = {
  "Aries": 'Овен',
  "Taurus": 'Телец',
  "Gemini": 'Близнецы',
  "Cancer": 'Рак',
  "Leo": 'Лев',
  "Virgo": 'Дева',
  "Libra": 'Весы',
  "Scorpio": 'Скорпион',
  "Sagittarius": 'Стрелец',
  "Capricorn": 'Козерог',
  "Aquarius": 'Водолей',
  "Pisces": 'Рыбы',

  "Lion": 'Лев',
}

PLANETS = {'Sun': 10,  'Mercury': 199, 'Venus': 299,
      'Mars': 499, 'Jupiter': 599, 'Saturn': 699,
      'Uranus': 799, 'Neptune': 899, 'Pluto': 999}

PREDICTIONS_DF = pd.read_csv("files/horoscopes3.csv", sep=";", index_col="date")
PREDICTIONS_DF_MIHA = pd.read_csv("files/horoscopes_miha.csv", sep=";", index_col="date")
USER_DICT = {}


logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}

# Предсказательные функции
def get_prediction_from_model(target_date, target_sign, oracle="vanga"):

  headers = {'Content-Type': 'application/json'}
  command_to_model = str(target_date) + ' ' + INV_SIGNS_DICT[target_sign]
  logging.info("command_to_model: %r", command_to_model)
  data = {"request":{"command": command_to_model, "oracle":oracle}, "version":23, "session":{"user_id":123}}
  resp = req.post(model_url, data=json.dumps(data), headers=headers)
  return(json.loads(resp.text)['response']['text'])

def get_prediction(target_date, target_sign, PREDICTIONS_DF=PREDICTIONS_DF, oracle="vanga"):
    if oracle == "vanga":
        if target_date in PREDICTIONS_DF.index:
            return(PREDICTIONS_DF.loc[target_date,target_sign])
        else:
            return(get_prediction_from_model(target_date, target_sign, oracle))
    elif oracle == "miha":
        if target_date in PREDICTIONS_DF_MIHA.index:
            logging.info("reading miha's file")
            return(PREDICTIONS_DF_MIHA.loc[target_date,target_sign])
        else:
            return(get_prediction_from_model(target_date, target_sign, oracle))

#
# Вторая версия сайта
# Все страницы в подпапке index
#

@application.route('/')
# Главная страница с общим прогнозом на сегодня и со всеми остальными вариантами прогнозов
@application.route('/index/<oracle>/<date>/<sign>', methods=['post', 'get'])
@application.route('/index')
@application.route('/index/<oracle>/<date>')
def index(sign='main_horo', oracle='vanga', date='today', version=23):
    logging.info("sign: %r", sign)
    logging.info("oracle: %r", oracle)
    sign_2 = sign.capitalize().lower()

    if oracle=='miha':
        version=33
        logging.info("version changed: %r", version)

    if request.method != 'POST':
        # 2020-11-22
        if sign != 'main_horo':
            sign = RU_EN_SIGNS[sign.capitalize()].lower()

        if date in ['today', 'custom']:
            dd = datetime.now()
            label = 'сегодня'
        if date == 'tomorrow':
            dd = datetime.now() + timedelta(days=1)
            label = 'завтра'
        if date == 'yesterday':
            dd = datetime.now() - timedelta(days=1)
            label = 'вчера'

        # day = '-'.join(map(str, [dd.year, dd.month, dd.day]))
        day = dd.strftime('%Y-%m-%d')
        # df = pd.read_csv("files/horoscopes.csv", sep=";")
        # main_horo = df.loc[df['date']==day][sign].values[0]
        logging.info("day: %r", day)
        main_horo = get_prediction(day,sign,PREDICTIONS_DF,oracle)
        if date == 'custom':
            main_horo = 'Выберите дату, а потом нажмите на нужный знак зодиака'
            day = ''
            # sign = ''
            label = 'произвольный день'
        return render_template("index.html", oracle=oracle, main_horo=main_horo, day=day, sign=sign.capitalize(), sign_2=sign_2, label=label, date=date)
    else:
        if sign != 'main_horo':
          sign = RU_EN_SIGNS[sign.capitalize()].lower()
        else:
          sign = 'рыбы'
        logging.info("sign: %r", sign)
        # user_sign = RU_EN_SIGNS[sign.capitalize()]

        date_of_horo = request.form.get('date2')
        date_of_horo = date_of_horo.replace('.', '-')
        date_of_horo = '-'.join(date_of_horo.split('-')[::-1])

        day = request.form.get('date2').replace('.', '-')

        logging.info("day: %r", date_of_horo)
        main_horo = get_prediction(date_of_horo,sign,PREDICTIONS_DF,oracle)
        label = 'произвольный день'
        return render_template("index.html", oracle=oracle, main_horo=main_horo, day=day, sign=sign.capitalize(), sign_2=sign_2, label=label, date=date)

# Рендер страницы экспертов
@application.route('/index/experts')
def experts():
    return render_template("experts.html")

# Рендер страницы справки api
@application.route("/index/api")
def api2():
  return render_template('api2.html')

@application.route("/web", methods=['POST'])
def web():
  logging.info("Request: %r", request.json)
  card = {}
  buttons = []
  date, sign_idx = request.json['request']['command'].split()
  text = get_prediction(date, SIGNS_DICT[sign_idx], PREDICTIONS_DF, request.json['request']['oracle'])
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


@application.route("/debug", methods=['POST'])
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
  application.run(debug=True)
