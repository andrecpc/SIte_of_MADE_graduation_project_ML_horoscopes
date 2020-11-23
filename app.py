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

test_model = HoroModel(gen_path='gen_500000',
                       gpt_path ='sberbank-ai/rugpt3small_based_on_gpt2', # 'sberbank-ai/rugpt3small_based_on_gpt2', 'sberbank-ai/rugpt3large_based_on_gpt2', 'model'
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
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
       [-9.11908546e-01, -4.02126265e-01,  2.35540374e-05,
         7.22533246e-03, -1.56840134e-02,  3.19168644e-07,
         5.75608779e-03,  9.96635706e-01, -2.82840242e-04,
        -5.51720439e-01, -4.76377605e-01, -3.90845170e-02,
         7.45404568e-03,  1.31309676e-02,  2.33397070e-03,
         4.21596486e-03,  7.29971687e-01, -1.43280494e-02,
        -1.14599852e+00,  2.77093314e-01,  2.28529004e-02,
        -1.19654852e-02, -2.23882399e-02,  1.01574528e-03,
         6.81074328e-03,  1.17924364e+00,  6.38715298e-03,
         3.97954095e-01,  1.43586422e-01, -2.06732541e-02,
         2.37916980e-03, -1.57175853e-03,  4.14943558e-04,
         2.44633876e-03,  4.23570426e-01,  1.68222072e-03,
         1.65730108e+00, -4.83300225e+00, -3.90553185e-02,
         1.36695174e-02, -1.15389669e-02, -1.61086708e-04,
         2.95094981e-02,  5.10941122e+00,  1.53498411e-02,
         4.24270854e+00, -8.96938478e+00, -5.61820403e-02,
         1.17021106e-02, -1.28176384e-02, -2.27791332e-04,
         5.73068791e-02,  9.92237853e+00,  1.65915634e-02,
         1.46265862e+01,  1.18396344e+01, -1.55799592e-01,
         4.76825764e-03, -1.27737792e-02,  4.26834303e-05,
         1.08686944e-01,  1.88185611e+01, -4.33084090e-03,
         2.85070438e+01, -5.87051564e+00, -5.65435654e-01,
         7.78468934e-03, -1.25736667e-02, -7.61588214e-05,
         1.68129517e-01,  2.91107234e+01,  1.01603607e-02,
         1.29248252e+01, -3.16071258e+01, -6.62255726e-01,
         1.01840408e-02, -1.50763755e-02, -9.26121637e-04,
         1.97257423e-01,  3.41540641e+01,  1.78239747e-02,
         1.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
       [-9.18996377e-01, -3.86382600e-01,  2.31578922e-05,
         6.94998940e-03, -1.58024334e-02,  4.76421240e-07,
         5.75771922e-03,  9.96918179e-01, -2.82099138e-04,
        -5.60073485e-01, -4.89207770e-01, -4.13037788e-02,
         9.23449109e-03,  1.25069672e-02,  2.10423335e-03,
         4.30154989e-03,  7.44790275e-01, -1.52759942e-02,
        -1.13380483e+00,  2.99269747e-01,  2.18281189e-02,
        -1.24196632e-02, -2.19629104e-02,  1.03368439e-03,
         6.77375543e-03,  1.17283940e+00,  6.42134203e-03,
         3.95644486e-01,  1.45189805e-01, -2.10871952e-02,
         2.23983517e-03, -1.63435020e-03,  4.12934087e-04,
         2.43709977e-03,  4.21970744e-01,  1.51711899e-03,
         1.64376621e+00, -4.82139900e+00, -3.88942744e-02,
         1.34000114e-02, -1.16671965e-02, -1.61015593e-04,
         2.94207922e-02,  5.09405226e+00,  1.53679142e-02,
         4.23114304e+00, -8.95650632e+00, -5.59542508e-02,
         1.14285666e-02, -1.29384331e-02, -2.27769397e-04,
         5.72110812e-02,  9.90579163e+00,  1.65813909e-02,
         1.46219551e+01,  1.18524676e+01, -1.55842350e-01,
         4.49355656e-03, -1.28917509e-02,  4.28157382e-05,
         1.08712814e-01,  1.88230403e+01, -4.62736881e-03,
         2.84993966e+01, -5.85788207e+00, -5.65359485e-01,
         7.50946321e-03, -1.26925951e-02, -7.62378007e-05,
         1.68071555e-01,  2.91006876e+01,  9.91076229e-03,
         1.29147774e+01, -3.15919941e+01, -6.61334571e-01,
         9.90972078e-03, -1.51873356e-02, -9.15219790e-04,
         1.97154484e-01,  3.41362407e+01,  1.78222707e-02,
         1.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
       [-9.25807885e-01, -3.70523170e-01,  2.25968055e-05,
         6.67272717e-03, -1.59155393e-02,  6.46819839e-07,
         5.75934636e-03,  9.97199910e-01, -2.81375230e-04,
        -5.70153637e-01, -5.01349471e-01, -4.32926296e-02,
         1.09076502e-02,  1.17567222e-02,  1.87342423e-03,
         4.39205561e-03,  7.60460856e-01, -1.60354978e-02,
        -1.12116371e+00,  3.21015770e-01,  2.07858030e-02,
        -1.28602905e-02, -2.15274884e-02,  1.05080951e-03,
         6.73657024e-03,  1.16640098e+00,  6.45547269e-03,
         3.93474811e-01,  1.46853804e-01, -2.14991109e-02,
         2.09934068e-03, -1.69298807e-03,  4.10890615e-04,
         2.42881442e-03,  4.20536180e-01,  1.35204100e-03,
         1.63050262e+00, -4.80966987e+00, -3.87332880e-02,
         1.31271132e-02, -1.17894380e-02, -1.60924424e-04,
         2.93319939e-02,  5.07867732e+00,  1.53806445e-02,
         4.21985206e+00, -8.94350964e+00, -5.57265308e-02,
         1.11530856e-02, -1.30540446e-02, -2.27665973e-04,
         5.71153566e-02,  9.88921744e+00,  1.65661270e-02,
         1.46175997e+01,  1.18654161e+01, -1.55885225e-01,
         4.21704714e-03, -1.30044310e-02,  4.29693741e-05,
         1.08740391e-01,  1.88278151e+01, -4.92179131e-03,
         2.84920253e+01, -5.84513230e+00, -5.65283117e-01,
         7.23279073e-03, -1.28059985e-02, -7.64906319e-05,
         1.68015042e-01,  2.90909028e+01,  9.65844384e-03,
         1.29050094e+01, -3.15767497e+01, -6.60425301e-01,
         9.62499742e-03, -1.53021907e-02, -9.04275604e-04,
         1.97051557e-01,  3.41184195e+01,  1.78203253e-02,
         1.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00,
         0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
       [-9.32341269e-01, -3.54553298e-01,  2.18643179e-05,
         6.39377842e-03, -1.60233195e-02,  8.17075218e-07,
         5.76096962e-03,  9.97480969e-01, -2.80769975e-04,
        -5.81852105e-01, -5.12684307e-01, -4.50507795e-02,
         1.24708181e-02,  1.08957117e-02,  1.64306345e-03,
         4.48645388e-03,  7.76805409e-01, -1.66273989e-02,
        -1.10808889e+00,  3.42321504e-01,  1.97267801e-02,
        -1.32870095e-02, -2.10824096e-02,  1.06709401e-03,
         6.69918837e-03,  1.15992851e+00,  6.48943077e-03,
         3.91446119e-01,  1.48574463e-01, -2.19089607e-02,
         1.95790461e-03, -1.74767291e-03,  4.08799955e-04,
         2.42148163e-03,  4.19266547e-01,  1.18730726e-03,
         1.61751136e+00, -4.79782143e+00, -3.85724269e-02,
         1.28547809e-02, -1.19072187e-02, -1.60829395e-04,
         2.92431332e-02,  5.06329155e+00,  1.53907129e-02,
         4.20883742e+00, -8.93040000e+00, -5.54989225e-02,
         1.08759438e-02, -1.31643777e-02, -2.27541543e-04,
         5.70197350e-02,  9.87266108e+00,  1.65457787e-02,
         1.46135216e+01,  1.18784746e+01, -1.55928370e-01,
         3.93874863e-03, -1.31117345e-02,  4.33317067e-05,
         1.08769662e-01,  1.88328832e+01, -5.21402765e-03,
         2.84849315e+01, -5.83227201e+00, -5.65206588e-01,
         6.95463710e-03, -1.29136282e-02, -7.64979445e-05,
         1.67959995e-01,  2.90813716e+01,  9.40331818e-03,
         1.28955285e+01, -3.15613888e+01, -6.59522715e-01,
         9.33685739e-03, -1.54195871e-02, -9.02923828e-04,
         1.96948638e-01,  3.41005995e+01,  1.78197100e-02,
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

    if request.json['choice'] == 'today':
        # Выдергиваем из csv 12 прогнозов на сегодня и записываем в словарь,
        # где ключи знаки, а прогнозы значения. Всё как в vanga_today.

        # Пока тут заглушка, и просто берется первая строка файла с 12 прогнозами
        horos = list(PREDICTIONS_DF[SIGNS][0:1].values[0])
        sig = [el.capitalize() for el in SIGNS]
        horos_dict = dict(zip(sig, horos))
        answer["horoscopes"] = horos_dict

    elif request.json['choice'] == 'custom':
        # Делаем предсказание по дате и определяем знак как в vanga_custom

        # Тут определяем знак зодиака
        d,m,y = request.json['period'][0].split('.')
        user_sign = get_zodiac_sign(d, m)
        user_sign = RU_EN_SIGNS[user_sign]

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
        answer["horoscope"] = str(test_results[0])

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
#

# Главная страница с общим прогнозом на сегодня
@app.route('/index')
@app.route('/index/<oracle>/<date>')
@app.route('/index/<oracle>/<date>/<sign>', methods=['post', 'get'])
def index(sign='main_horo', oracle='vanga', date='today'):

    if request.method != 'POST':
        # 2020-11-22
        if sign != 'main_horo':
            sign = RU_EN_SIGNS[sign.capitalize()].lower()

        if date in ['today' , 'custom']:
            dd = datetime.now()
            label = 'сегодня'
        if date == 'tomorrow':
            dd = datetime.now() + timedelta(days=1)
            label = 'завтра'
        if date == 'yesterday':
            dd = datetime.now() - timedelta(days=1)
            label = 'вчера'

        day = '-'.join(map(str,[dd.year, dd.month, dd.day]))
        df = pd.read_csv("files/horoscopes.csv", sep=";")
        main_horo = df.loc[df['date']==day][sign].values[0]

        if date == 'custom':
            main_horo = 'Выберите дату, а потом нажмите на нужный знак зодиака'
            day = ''
            # sign = ''
            label = 'произвольный день'
        return render_template("index.html", main_horo=main_horo, day=day, sign=sign.capitalize(), label=label, date=date)
    else:
        date_of_horo = request.form.get('date2')
        date_of_horo = date_of_horo.replace('.', '-')
        date_of_horo = '-'.join(date_of_horo.split('-')[::-1])

        main_horo = 'Заглушка прогноза для даты '+ str(date_of_horo)
        day = ''
        sign = ''
        label = 'произвольный день'
        return render_template("index.html", main_horo=main_horo, day=day, sign=sign.capitalize(), label=label, date=date)

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
