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
from datetime import date, timedelta
# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request, render_template, request
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

		answer["detected_sign"] = user_sign
		answer["horoscope"] = str(predicted_horo)

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

	return render_template('vanga_custom.html', dates = [user_sign, predicted_horo])

# Далее идут Марусины причиндалы
@app.route("/marusya", methods=['POST', 'GET'])
def marusya():
	return "Marusya"

@app.route("/web", methods=['POST'])
def web():
	logging.info("Request: %r", request.json)
	card = {}
	buttons = []
	date, sign = request.json['request']['command'].split()
	USER_DICT[request.json['session']['user_id']] = sign
	text = get_prediction(date, USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
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
		buttons = [{"title":"На завтра"}, {"title":"На другую дату"}]

	elif request.json['request']['command'] == 'на завтра':
		tomorrow_date = date.today() + timedelta(days=1)
		if request.json['session']['user_id'] in USER_DICT:
			text = "Гороскоп на завтра. \n"+get_prediction(str(tomorrow_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
			buttons = [{"title":"На сегодня"}, {"title":"На другую дату"}]
		else:
			text = "Какой у Вас знак зодиака?"

	elif request.json['request']['command'] == 'на сегодня':
		today_date = date.today()
		if request.json['session']['user_id'] in USER_DICT:
			text = "Гороскоп на сегодня. \n"+get_prediction(str(today_date), USER_DICT[request.json['session']['user_id']], PREDICTIONS_DF)
			buttons = [{"title":"На завтра"}, {"title":"На другую дату"}]
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
