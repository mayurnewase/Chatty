import os
from StringIO import StringIO

from bson.json_util import dumps
from bson.json_util import loads
from bson.objectid import ObjectId
from flask import Blueprint, request, Response
from flask import abort
from flask import current_app as app
from flask import send_file

from app.commons import build_response

from app.seats.models import Seats
#get full map		get
#update full map	post

seats_blueprint = Blueprint("seats_blueprint", __name__, url_prefix = "/seats")

@seats_blueprint.route("/<id>", methods = ["GET"])
def get_map(id):
	print("-----Seat get_map hit for id " ,str(id))
	full_map = Seats.objects(_id = str(id))
	print("full map is", full_map)
	return build_response.sent_json(full_map.to_json())


@seats_blueprint.route("/", methods = ["POST"])
def set_map():
	content = request.get_json(silent = True)
	print(type(content), content.keys())
	#print(content)
	print("--Seats set_map post hit")

	seat_map_new = Seats()	
	seat_map_new.all_seats = content.get(u"seat_map")
	seat_map_new._id = content.get(u"id")

	try:
		ret_id = seat_map_new.save()	
	except Exception as e:
		return build_response.build_json("error "+ str(e))
	print("--Success")
	return build_response.sent_ok()


@seats_blueprint.route("/update", methods = ["POST"])
def update_map():
	content = request.get_json(silent = True)
	print(type(content))
	print(content)
	print("--Seats update post hit")

	#seat_map_new = Seats()	
	#seat_map_new.all_seats = content
	seat_map_new = Seats()	
	
	seat_map_new.all_seats = content
	seat_map_new._id = str(ObjectId())

	try:
		#ret_id = objects.delete()
		ret_id = seat_map_new.save()
	except Exception as e:
		return build_response.build_json("error " + str(e))
	print("--Success", seat_map_new._id)

	return build_response.sent_json((seat_map_new._id))





















