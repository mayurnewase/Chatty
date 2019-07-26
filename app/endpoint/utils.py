"""
File to support controller
"""

import json

import requests
from jinja2 import Undefined

from app import app
from app.entities.models import Entity

def treat_intent(intent, params, seat_map):
	"""
	just read intent and call that function
	"""

	print("----TREATING INTENT WITH PARAMS", intent, params, seat_map)
	if intent == "book_seats":
		seat_map = book_seats(params, seat_map)
	return seat_map

def book_seats(params, seat_map):
	"""
	for now book only one seat

	should handle:
		seats not free
		params can contain range of seats
		check invalid seats numbers

	params should have:
		seat numbers to book
		seat range to book
	seat_map

	return seat_map
	
	{
		"_id" : "all_full", 
		"all_seats":
					[
						{
							"seatRowLabel" : "A",
							"seats":
									[
										{
											"status" : "available",
											"seatLabel" : "A 1",
											"seatNo" : "1",
											"key" : "A_1"
										},
										{
											"status":"available",
											"seatLabel" : "A 2",
											"seatNo" : "2",
											"key" : "A_2" },
										{
											"status":"available",
											"seatLabel":"B 4",
											"seatNo":"4",
											"key":"B_4"
										}
									] 
						}
					]
	}
	"""
	#book single seat
		#check status
		#return result
	print("--params is ",params)
	seat_row = params[0][0]
	seat_no = params[1][1:]
	#seat_map is faulty -> so usig loop to find row
	for row_index, dict_ in enumerate(seat_map):
		if dict_["seatRowLabel"] == seat_row:
			all_seats = dict_["seats"]
			for seat_index, seat in enumerate(all_seats):
				if seat["seat_no"] == seat_no:
					status = seat["status"]
					break

	if status == "available":
		seat_map[row_index]["seats"][seat_index][status] = "booked"

	return seat_map


def split_sentence(sentence):
	return sentence.split("###")


def get_synonyms():
	"""
	Build synonyms dict from DB
	:return:
	"""
	synonyms = {}

	for entity in Entity.objects:
		for value in entity.entity_values:
			for synonym in value.synonyms:
				synonyms[synonym] = value.value
	app.logger.info("loaded synonyms %s", synonyms)
	return synonyms


def call_api(url, type, headers={}, parameters={}, is_json=False):
	"""
	Call external API
	:param url:
	:param type:
	:param parameters:
	:param is_json:
	:return:
	"""
	app.logger.info("Initiating API Call with following info: url => {} payload => {}".format(url, parameters))
	if "GET" in type:
		response = requests.get(url, headers=headers, params=parameters, timeout=5)
	elif "POST" in type:
		if is_json:
			response = requests.post(url, headers=headers, json=parameters, timeout=5)
		else:
			response = requests.post(url, headers=headers, params=parameters, timeout=5)
	elif "PUT" in type:
		if is_json:
			response = requests.put(url, headers=headers, json=parameters, timeout=5)
		else:
			response = requests.put(url, headers=headers, params=parameters, timeout=5)
	elif "DELETE" in type:
		response = requests.delete(url, headers=headers, params=parameters, timeout=5)
	else:
		raise Exception("unsupported request method.")
	result = json.loads(response.text)
	app.logger.info("API response => %s", result)
	return result


class SilentUndefined(Undefined):
	"""
	Class to suppress jinja2 errors and warnings
	"""

	def _fail_with_undefined_error(self, *args, **kwargs):
		return 'undefined'

	__add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
		__truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
		__mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
		__getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
		__float__ = __complex__ = __pow__ = __rpow__ = \
		_fail_with_undefined_error
