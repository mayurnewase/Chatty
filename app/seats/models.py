from bson.objectid import ObjectId
from mongoengine.fields import BooleanField
from mongoengine.fields import Document
from mongoengine.fields import EmbeddedDocument
from mongoengine.fields import EmbeddedDocumentField
from mongoengine.fields import EmbeddedDocumentListField
from mongoengine.fields import ListField
from mongoengine.fields import ObjectIdField
from mongoengine.fields import StringField



class seats(Document):
	all_seats = ListField(required = True)













































