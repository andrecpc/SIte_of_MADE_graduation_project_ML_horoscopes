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
# import locale

from datetime import datetime, date, timedelta
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request, render_template, request
application = Flask(__name__)

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

PREDICTIONS_DF = pd.read_csv("files/horoscopes.csv", sep=";", index_col="date")
USER_DICT = {}

app = Flask(__name__)
app.debug = True

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}

# Предсказательные функции
def get_prediction_from_model(target_date, target_sign):
  
  headers = {'Content-Type': 'application/json'}
  command_to_model = str(target_date) + ' ' + INV_SIGNS_DICT[target_sign]
  logging.info("command_to_model: %r", command_to_model)
  data = {"request":{"command": command_to_model}, "version":23, "session":{"user_id":123}}
  resp = req.post(model_url, data=json.dumps(data), headers=headers)
  return(json.loads(resp.text)['response']['text'])

def get_prediction(target_date, target_sign, PREDICTIONS_DF=PREDICTIONS_DF):
  if target_date in PREDICTIONS_DF.index:
    return(PREDICTIONS_DF.loc[target_date,target_sign])
  else:
    return(get_prediction_from_model(target_date, target_sign))

#
# Первая версия сайта
#

# Рендер главной страницы
@app.route("/")
def hello():
  '''Тут всё шикарно. Никакой логики, переменных или чего-то еще.
  Просто рендерим шаблон главной страницы.'''

  return render_template('main.html')

# Рендер страницы справки api
@app.route("/api")
def api():
  '''Тут всё шикарно. Никакой логики, переменных или чего-то еще.
  Просто рендерим шаблон страницы.'''

  return render_template('api.html')

# Обработчик запросов к api
@app.route("/api-request", methods=['POST'])
def api_request():
    '''На странице /api есть документация. Здесь надо сделать тот же
    функционал, что и для страницы vanga_custom, только на выходе
    не будем рендерить страницу, а просто возвращать ответ с запрашиваемой
    информацией.'''

    logging.info("Request: %r", request.json)
    answer = {}

    if request.json['choice'] in ['today', 'tomorrow', 'yesterday']:

        date = request.json['choice']

        if date == 'today':
            dd = datetime.now()
        if date == 'tomorrow':
            dd = datetime.now() + timedelta(days=1)
        if date == 'yesterday':
            dd = datetime.now() - timedelta(days=1)

        day = '-'.join(map(str, [dd.year, dd.month, dd.day]))
        df = pd.read_csv("files/horoscopes.csv", sep=";")
        horos = list(df.loc[df['date']==day][SIGNS].values[0])

        # Выдергиваем из csv 12 прогнозов на сегодня и записываем в словарь,
        # где ключи знаки, а прогнозы значения. Всё как в vanga_today.

        # Пока тут заглушка, и просто берется первая строка файла с 12 прогнозами
        # horos = list(PREDICTIONS_DF[SIGNS][0:1].values[0])
        sig = [el.capitalize() for el in SIGNS]
        horos_dict = dict(zip(sig, horos))
        answer["date"] = day
        answer["horoscopes"] = horos_dict

    elif request.json['choice'] == 'custom':
        # Делаем предсказание по дате и определяем знак как в vanga_custom

        # Тут определяем знак зодиака
        # d,m,y = request.json['period'][0].split('.')
        # user_sign = get_zodiac_sign(d, m)
        # user_sign = RU_EN_SIGNS[user_sign]
        user_sign = RU_EN_SIGNS[request.json['period'][0].capitalize()]

        # Тут готовим фрейм с координатами планет по дате
        date_of_horo = request.json['period'][1].replace('.', '-')
        date_of_horo = '-'.join(date_of_horo.split('-')[::-1])
        date_for_epoch = Time(date_of_horo).jd
        # Фрейм с координатами планет под выбранную дату (shape (1, 81))
        df_planets = pd.read_csv("files/planets_template.csv", sep=";")
        for k, v in PLANETS.items():
            kk = [k+'_x',k+'_y',k+'_z',k+'_vx',k+'_vy',k+'_vz',k+'_l',k+'_ry',k+'_rr']
            df_planets.loc[0, kk] = Horizons(id=v, location=500, epochs=date_for_epoch, id_type='id').vectors().to_pandas()[['x','y','z','vx','vy','vz','lighttime','range','range_rate']].values[0]

        # Тут готовим ohe фрейм для знака
        cls_cols = [el.capitalize() + '_cls' for el in SIGNS]
        # Фрейм с ohe знака
        df_ohe = pd.DataFrame(columns=cls_cols)
        df_ohe.loc[0] = [0,0,0,0,0,0,0,0,0,0,0,0]
        df_ohe[user_sign + '_cls'] = 1

        # Тут конкатим итоговый фрейм фич.
        features_df = pd.concat([df_planets,df_ohe],axis=1)

        # В эту переменную потом надо положить финальный прогноз, пока тут заглушка из фич
        predicted_horo = features_df.values[0][1:]
        test_results = test_model.get_prediction(np.array([predicted_horo]))
        answer["detected_sign"] = user_sign
        answer["horoscope"] = str('.'.join(test_results[0].split('.')[0:-1]) + '.')

    logging.info("response %r", answer)

    return json.dumps (answer, ensure_ascii=False, indent=2)

# Рендер прогнозов Ванги из файла на сегодня
@app.route("/vanga_today")
def vanga_today():
  '''На выходе нужен словарь horos_dict с ключами знаками и значениями —
  предсказанными гороскопами на сегодня. Логика забора данных из
  датафрейма будет зависить от самого файла. Либо в нем будет всего 12
  гороскопов на сегодня, и тогда можно брать сразу всё, либо в нем будет
  разметка по датам, и тогда надо фильтровать по дате. Сегодняшнюю дату
  можно брать из встроенного питовского time.'''

  # Пока тут заглушка, и просто берется первая строка файла с 12 прогнозами
  horos = list(PREDICTIONS_DF[SIGNS][0:1].values[0])
  sig = [el.capitalize() for el in SIGNS]
  horos_dict = dict(zip(sig, horos))
  return render_template('vanga_today.html', horos_dict=horos_dict)

# Рендер прогнозов Ванги на произвольную дату
@app.route("/vanga_custom", methods=['post', 'get'])
def vanga_custom():
  '''Принимает из запроса 2 даты: день рождения и нужный день прогноза.
  Если значения пришли некорректные, то рендерим страницу с посылом о
  выборе дат.
  Если значения пришли нормальные, то определяем знак зодиака по первой дате
  и готовим фичи для GANа по второй дате.
  На выходе отдаем рендер страницы, переменную со знаком и предсказание.
  Пока на предсказание стоит заглушка из фичей в виде координат планет+ohe.'''

  # Тут проверку входных дат делаем
  date_of_BD = ""
  date_of_horo = ""
  if request.method == 'POST':
    date_of_BD = request.form.get('date1')
    date_of_horo = request.form.get('date2')
  if date_of_BD == "дд-мм-гггг":
    return render_template('vanga_custom.html', dates = False)
  if date_of_BD == "":
    return render_template('vanga_custom.html', dates = False)

  # Тут определяем знак зодиака
  # locale.setlocale(locale.LC_ALL, 'ru_RU')
  d,m,y = date_of_BD.split('.')
  user_sign = get_zodiac_sign(d, m)
  user_sign = RU_EN_SIGNS[user_sign]
  date_of_BD = ""

  # Тут готовим фрейм с координатами планет по дате
  date_of_horo = date_of_horo.replace('.', '-')
  date_of_horo = '-'.join(date_of_horo.split('-')[::-1])
  date_for_epoch = Time(date_of_horo).jd
  # Фрейм с координатами планет под выбранную дату (shape (1, 81))
  df_planets = pd.read_csv("files/planets_template.csv", sep=";")
  for k, v in PLANETS.items():
    kk = [k+'_x',k+'_y',k+'_z',k+'_vx',k+'_vy',k+'_vz',k+'_l',k+'_ry',k+'_rr']
    df_planets.loc[0, kk] = Horizons(id=v, location=500, epochs=date_for_epoch, id_type='id').vectors().to_pandas()[['x','y','z','vx','vy','vz','lighttime','range','range_rate']].values[0]

  # Тут готовим ohe фрейм для знака
  cls_cols = [el.capitalize() + '_cls' for el in SIGNS]
  # Фрейм с ohe знака
  df_ohe = pd.DataFrame(columns=cls_cols)
  df_ohe.loc[0] = [0,0,0,0,0,0,0,0,0,0,0,0]
  df_ohe[user_sign + '_cls'] = 1

  # Тут конкатим итоговый фрейм фич.
  features_df = pd.concat([df_planets,df_ohe],axis=1)

  # В эту переменную потом надо положить финальный прогноз, пока тут заглушка из фич
  predicted_horo = features_df.values[0][1:]

  # Тут начинается работа моделей
  test_results = test_model.get_prediction(np.array([predicted_horo]))
  # test_results = test_model.get_prediction(test)

  return render_template('vanga_custom.html', dates = [user_sign, test_results[0]])

#
# Вторая версия сайта
# Все страницы в подпапке index
#

# Главная страница с общим прогнозом на сегодня и со всеми остальными вариантами прогнозов
@app.route('/index/<oracle>/<date>/<sign>', methods=['post', 'get'])
@app.route('/index')
@app.route('/index/<oracle>/<date>')
def index(sign='main_horo', oracle='vanga', date='today'):
    logging.info("sign: %r", sign)
    sign_2 = sign.capitalize().lower()
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

        day = '-'.join(map(str, [dd.year, dd.month, dd.day]))
        # df = pd.read_csv("files/horoscopes.csv", sep=";")
        # main_horo = df.loc[df['date']==day][sign].values[0]
        logging.info("day: %r", day)
        main_horo = get_prediction(day,sign,PREDICTIONS_DF)
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

        # date_for_epoch = Time(date_of_horo).jd
        # Фрейм с координатами планет под выбранную дату (shape (1, 81))
        # df_planets = pd.read_csv("files/planets_template.csv", sep=";")
        # for k, v in PLANETS.items():
        #   kk = [k+'_x',k+'_y',k+'_z',k+'_vx',k+'_vy',k+'_vz',k+'_l',k+'_ry',k+'_rr']
        #   df_planets.loc[0, kk] = Horizons(id=v, location=500, epochs=date_for_epoch, id_type='id').vectors().to_pandas()[['x','y','z','vx','vy','vz','lighttime','range','range_rate']].values[0]

        # # Тут готовим ohe фрейм для знака
        # cls_cols = [el.capitalize() + '_cls' for el in SIGNS]
        # # Фрейм с ohe знака
        # df_ohe = pd.DataFrame(columns=cls_cols)
        # df_ohe.loc[0] = [0,0,0,0,0,0,0,0,0,0,0,0]
        # df_ohe[user_sign + '_cls'] = 1

        # # Тут конкатим итоговый фрейм фич.
        # features_df = pd.concat([df_planets,df_ohe],axis=1)

        # # В эту переменную потом надо положить финальный прогноз, пока тут заглушка из фич
        # predicted_horo = features_df.values[0][1:]

        # # Тут начинается работа моделей
        # test_results = test_model.get_prediction(np.array([predicted_horo]))
        # test_results = test_model.get_prediction(test)

        # main_horo = 'Заглушка прогноза для даты '+ str(date_of_horo) + ' для знака ' + str(RU_EN_SIGNS[sign.capitalize()].lower())
        # main_horo = '.'.join(test_results[0].split('.')[0:-1]) + '.'

        day = request.form.get('date2').replace('.', '-')

        logging.info("day: %r", date_of_horo)
        main_horo = get_prediction(date_of_horo,sign,PREDICTIONS_DF)
        # sign = ''
        # if sign != 'main_horo':
        #     sign = RU_EN_SIGNS[sign.capitalize()].lower()
        label = 'произвольный день'
        return render_template("index.html", oracle=oracle, main_horo=main_horo, day=day, sign=sign.capitalize(), sign_2=sign_2, label=label, date=date)

# Рендер страницы экспертов
@app.route('/index/experts')
def experts():
    return render_template("experts.html")

# Рендер страницы справки api
@app.route("/index/api")
def api2():
  return render_template('api2.html')

# Далее идут Марусины причиндалы
@app.route("/marusya", methods=['POST', 'GET'])
def marusya():
  return "Marusya"

@app.route("/web", methods=['POST'])
def web():
  logging.info("Request: %r", request.json)
  card = {}
  buttons = []
  date, sign_idx = request.json['request']['command'].split()
  text = get_prediction(date, SIGNS_DICT[sign_idx], PREDICTIONS_DF)
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
    buttons = [{"title":"На завтра"}, {"title":"На другую дату"}, {"title":"Другой знак"}]

  elif request.json['request']['command'] == 'на завтра':
    tomorrow_date = date.today() + timedelta(days=1)
    if request.json['session']['user_id'] in USER_DICT:
      text = "Гороскоп на завтра. \n"+get_prediction(str(tomorrow_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
      buttons = [{"title":"На сегодня"}, {"title":"На другую дату"}, {"title":"Другой знак"}]
    else:
      text = "Какой у Вас знак зодиака?"

  elif request.json['request']['command'] == 'другой знак':
        text = "Какой знак зодиака Вас интересует?"

  elif request.json['request']['command'] == 'на сегодня':
    today_date = date.today()
    if request.json['session']['user_id'] in USER_DICT:
      text = "Гороскоп на сегодня. \n"+get_prediction(str(today_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
      buttons = [{"title":"На завтра"}, {"title":"На другую дату"}, {"title":"Другой знак"}]
    else:
      text = "Какой у Вас знак зодиака?"

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
