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
		seat_map, response = book_seats(params, seat_map)

	if intent == "search_free_seats":
		seat_map, response = find_free_seats(params, seat_map)

	return seat_map, response

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
	#print("--params is ",params)
	seat_row = params["seat_no"][0]
	seat_no = int(params["seat_no"][1:])
	#print("seat row and no", seat_row, seat_no)
	status = None
	found = False
	seat_row_to_change = None
	seat_index_to_change = None


	#seat_map is faulty -> so usig loop to find row
	for row_index, dict_ in enumerate(seat_map):
		if dict_["seatRowLabel"] == seat_row:
			all_seats = dict_["seats"]
			for seat_index, seat in enumerate(all_seats):

				if int(seat["seatNo"]) == seat_no:
					#print("=================found seat here ", seat_no, seat["seatNo"])
					status = seat["status"]
					#print("==================status is ", status)
					#print("============== row and seat index", row_index, seat_index)
					found = True
					seat_row_to_change = row_index
					seat_index_to_change = seat_index
					break

	if found:
		#print("=================changing seat status===================")
		#print("=======row and seat index", row_index, seat_index)
		if (seat_map[seat_row_to_change]["seats"][seat_index_to_change]["status"] == "available"):
			seat_map[seat_row_to_change]["seats"][seat_index_to_change]["status"] = "booked"
			response = "booked successfully"
		else:
			response = "seat already booked"

	return seat_map, response

def find_free_seats(params, seat_map):
	"""
	param should have row number and how many seats
	so we will find it in that row

	return seat_map, response
	"""
	print("======inside find free seats====")	
	print("params are ", params)
	row = params["row"]
	total_seats_to_book = int(params["total_seats_to_book"])
	free_seat_found = []
	
	for row_index, dict_ in enumerate(seat_map):
		if dict_["seatRowLabel"] == row:
			print("found row to be checked")
			free_found = 0

			for seat_index, seat in enumerate(all_seats):
				if seat["status"] == "available":
					free_found += 1
					free_seat_found.append(seat_index)

					if free_found == total_seats_to_book:
						break
			
	if free_found == total_seats_to_book:
		for seat in free_seat_found:
			seat_map[row]["seats"][seat]["status"] == "booked"
		response = "booked successfully"
	else:
		response = "not enough free seats"

	return seat_map, response



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
