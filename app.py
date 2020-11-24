# -*- coding: utf-8 -*-


from __future__ import unicode_literals
import logging
import pandas as pd
from zodiac_sign import get_zodiac_sign
from astropy.time import Time
from astroquery.jplhorizons import Horizons
# import locale
import json
import logging
from datetime import datetime, date, timedelta
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request, render_template, request
application = Flask(__name__)

import numpy as np

from generate_transformers_4 import HoroModel

# Веса моделей
# simple https://drive.google.com/drive/folders/1qkL5tjQWMcJ2vEfMCMxOcvlui9MceXFP
# medium https://drive.google.com/drive/folders/1HpCJ6E1uZvTTgjJAhOUuY2XLhO8ZXu6z
# large https://drive.google.com/drive/folders/1k1wh6HIYU_NBK19itdCbi4sae6e7_ngP

test_model = HoroModel(gen_path='gen_500000',
                       gpt_path = 'sberbank-ai/rugpt3small_based_on_gpt2', # 'sberbank-ai/rugpt3small_based_on_gpt2', 'sberbank-ai/rugpt3large_based_on_gpt2', 'model/simple'
                       scaler_path = 'datatransformer.pickle',
                       kv_path = "model_rusvectores.model")

test = np.array([[-9.04546430e-01, -4.17748878e-01,  2.38048487e-05,
         7.49852345e-03, -1.55603482e-02,  1.87672386e-07,
         5.75445232e-03,  9.96352533e-01, -2.83478578e-04,
        -5.45199613e-01, -4.62993467e-01, -3.66367909e-02,
         5.57102562e-03,  1.36120381e-02,  2.56083748e-03,
         4.13644793e-03,  7.16203758e-01, -1.31714285e-02,
        -1.15773141e+00,  2.54496757e-01,  2.38593471e-02,
        -1.14981276e-02, -2.28031021e-02,  9.97018852e-04,
         6.84753376e-03,  1.18561372e+00,  6.35301037e-03,
         4.00402366e-01,  1.42047587e-01, -2.02573152e-02,
         2.51712582e-03, -1.50526949e-03,  4.16931550e-04,
         2.45653055e-03,  4.25335080e-01,  1.84700806e-03,
         1.67110522e+00, -4.84447457e+00, -3.92164066e-02,
         1.39378035e-02, -1.14042461e-02, -1.61073246e-04,
         2.95980886e-02,  5.12475018e+00,  1.53266853e-02,
         4.25454661e+00, -8.98213988e+00, -5.64098150e-02,
         1.19736740e-02, -1.26916878e-02, -2.27757868e-04,
         5.74027212e-02,  9.93897307e+00,  1.65966762e-02,
         1.46314909e+01,  1.18269218e+01, -1.55756943e-01,
         5.04074977e-03, -1.26505387e-02,  4.26581528e-05,
         1.08662792e-01,  1.88143792e+01, -4.03254824e-03,
         2.85149653e+01, -5.88302774e+00, -5.65511943e-01,
         8.05801347e-03, -1.24497378e-02, -7.64796960e-05,
         1.68188911e-01,  2.91210073e+01,  1.04068989e-02,
         1.29351421e+01, -3.16221459e+01, -6.63183494e-01,
         1.04485438e-02, -1.49625070e-02, -9.27382882e-04,
         1.97360357e-01,  3.41718865e+01,  1.78191802e-02,
         1.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00]])

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

# Заглушки для предсказательных функций
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
        df = pd.read_csv("files/horoscopes.csv", sep=";")
        main_horo = df.loc[df['date']==day][sign].values[0]

        if date == 'custom':
            main_horo = 'Выберите дату, а потом нажмите на нужный знак зодиака'
            day = ''
            # sign = ''
            label = 'произвольный день'
        return render_template("index.html", oracle=oracle, main_horo=main_horo, day=day, sign=sign.capitalize(), sign_2=sign_2, label=label, date=date)
    else:
        user_sign = RU_EN_SIGNS[sign.capitalize()]
        date_of_horo = request.form.get('date2')
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

        # main_horo = 'Заглушка прогноза для даты '+ str(date_of_horo) + ' для знака ' + str(RU_EN_SIGNS[sign.capitalize()].lower())
        main_horo = '.'.join(test_results[0].split('.')[0:-1]) + '.'
        day = request.form.get('date2').replace('.', '-')
        # sign = ''
        if sign != 'main_horo':
            sign = RU_EN_SIGNS[sign.capitalize()].lower()
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
