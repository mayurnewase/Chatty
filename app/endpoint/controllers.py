# -*- coding: utf-8 -*-

import json

from flask import Blueprint, request, abort
from jinja2 import Template

from app import app
from app.agents.models import Bot
from app.commons import build_response
from app.endpoint.utils import SilentUndefined
from app.endpoint.utils import call_api
from app.endpoint.utils import get_synonyms
from app.endpoint.utils import split_sentence, treat_intent
from app.intents.models import Intent
from app.nlu.classifiers.starspace_intent_classifier import \
    EmbeddingIntentClassifier
from app.nlu.entity_extractor import EntityExtractor
from app.nlu.tasks import model_updated_signal

endpoint = Blueprint('api', __name__, url_prefix='/api')

sentence_classifier = None
synonyms = None
entity_extraction = None

# Request Handler
@endpoint.route('/v1', methods=['POST'])
def api():
    """
    Endpoint to converse with chatbot.
    Chat context is maintained by exchanging the payload between client and bot.

    sample input/output payload =>

    {
      "currentNode": "",
      "complete": false,
      "parameters": [],
      "extractedParameters": {},
      "missingParameters": [],
      "intent": {},
      "context": {},
      "input": "hello",
      "speechResponse": [],
      "seat_map" : []
    }

    :param json:
    :return json:
    """

    #GET JSON FROM POST REQUEST

    request_json = request.get_json(silent=True)
    result_json = request_json
    print("-------------chat input is ", request_json.get("input"))
    seat_map = request_json.get("seat_map")             #PROBLEM -> seat_map is null,but keys in request json has seat_map sometimes
    print("----seat map in backend is ", seat_map)

    if request_json:

        #dont know what is context yet
        context = {"context": request_json["context"]}
        app.logger.info("-----context is ", context)

        #if input contain "init_conversation" then send fixed result_json -> dont predict anything
        if app.config["DEFAULT_WELCOME_INTENT_NAME"] in request_json.get("input"):

            intent = Intent.objects(
                intentId=app.config["DEFAULT_WELCOME_INTENT_NAME"]).first()
            result_json["complete"] = True
            result_json["intent"]["object_id"] = str(intent.id)
            result_json["intent"]["id"] = str(intent.intentId)
            result_json["input"] = request_json.get("input")
            template = Template(
                intent.speechResponse,
                undefined=SilentUndefined)
            result_json["speechResponse"] = split_sentence(template.render(**context))

            app.logger.info(request_json.get("input"), extra=result_json)
            return build_response.build_json(result_json)

            #predict intent id from intent model
            #get intentid
            #confidence for that intet
            #other intent with low confidence

        intent_id, confidence, suggestions = predict(request_json.get("input"))
        
        print("-----keys in request_json", request_json.keys())
        
        app.logger.info("intent_id => %s" % intent_id)

        #get predicted intent object from mongo,which contains
            #_id, intent_id, api_trigger, name,
            #parameters = [parameter_name, type, required compulsary, message to ask this parameter]
            #speech response = how to show result when all parameters provided
            #training data =  [ {"text" : "hello there", "entities":[]},  {"text" : "hello there", "entities":[]}, ....]
            #userdefined = true.false

        intent = Intent.objects.get(intentId=intent_id)

        if intent.parameters:
            parameters = intent.parameters
        else:
            parameters = []

        #for first request -> doesnt have param -> so None
        #First request after init response is always complete -> then it is inspected and decided if complete or not
        #So path is always:
            #first -> third (if no param required)
            #first -> second ->third   (if 1 param required)
            #first -> second -> second ->third   (if 2 params required)

        if ((request_json.get("complete") is None) or (request_json.get("complete") is True)):

            print("----FIRST PATH FOR REQUEST_JSON -> None || True")

            result_json["intent"] = {
                "object_id": str(intent.id),
                "confidence": confidence,
                "id": str(intent.intentId.encode('utf8'))
            }

            #if intent require parameters then extract them from input with entity extractor model -> crfsuit
            #else result_json is complete
            if parameters:

                # Extract NER entities
                app.logger.info("---entity extracting in first path")

                extracted_parameters = entity_extraction.predict(
                    intent_id, request_json.get("input"))

                print("---entity extracted is ", extracted_parameters)

                #find missing parameters and fill result_json
                missing_parameters = []
                result_json["missingParameters"] = []
                result_json["extractedParameters"] = {}
                result_json["parameters"] = []

                for parameter in parameters:
                    result_json["parameters"].append({
                        "name": parameter.name,
                        "type": parameter.type,
                        "required": parameter.required
                    })

                    if parameter.required:
                        if parameter.name not in extracted_parameters.keys():
                            result_json["missingParameters"].append(
                                parameter.name)
                            missing_parameters.append(parameter)

                result_json["extractedParameters"] = extracted_parameters

                #if missing some parameters:
                    #mark result_json as not complete
                    #set current node to first missing parameter
                    #put that paramter asking response in result_json
                if missing_parameters:
                    result_json["complete"] = False
                    current_node = missing_parameters[0]
                    result_json["currentNode"] = current_node["name"]
                    result_json["speechResponse"] = split_sentence(current_node["prompt"])
                    print("---result json in missing parameter", result_json)

                else:
                    result_json["complete"] = True
                    context["parameters"] = extracted_parameters
                    print("---result json in no missing parameter", result_json)

            else:
                result_json["complete"] = True

        elif request_json.get("complete") is False:
            #if some params are required further
            #and it is not cancel intent
            print("----SECOND PATH FOR REQUEST_JSON -> False")

            if "cancel" not in intent.name:

                intent_id = request_json["intent"]["id"]
                intent = Intent.objects.get(intentId=intent_id)

                #print("---request json in complete false is ", intent_id, request_json)
                print("----SECOND TIME ENTITY EXTRACTION WITH REPLACING SYNONYMS FOR ",
                    request_json.get("currentNode"),request_json.get("input"))

                extracted_parameter = entity_extraction.replace_synonyms({
                    request_json.get("currentNode"): request_json.get("input")
                })

                # replace synonyms for entity values
                result_json["extractedParameters"].update(extracted_parameter)

                result_json["missingParameters"].remove(
                    request_json.get("currentNode"))

                if len(result_json["missingParameters"]) == 0:
                    result_json["complete"] = True
                    context = {"parameters": result_json["extractedParameters"],
                               "context": request_json["context"]}
                else:
                    missing_parameter = result_json["missingParameters"][0]
                    result_json["complete"] = False
                    current_node = [
                        node for node in intent.parameters if missing_parameter in node.name][0]
                    result_json["currentNode"] = current_node.name
                    result_json["speechResponse"] = split_sentence(current_node.prompt)
            else:
                result_json["currentNode"] = None
                result_json["missingParameters"] = []
                result_json["parameters"] = {}
                result_json["intent"] = {}
                result_json["complete"] = True

        if result_json["complete"]:
            print("----THIRD PATH FOR RESULT_JSON -> True")

            if intent.apiTrigger:
                isJson = False
                parameters = result_json["extractedParameters"]
                headers = intent.apiDetails.get_headers()
                app.logger.info("headers %s" % headers)
                url_template = Template(
                    intent.apiDetails.url, undefined=SilentUndefined)
                rendered_url = url_template.render(**context)

                if intent.apiDetails.isJson:
                    isJson = True
                    request_template = Template(
                        intent.apiDetails.jsonData, undefined=SilentUndefined)
                    parameters = json.loads(request_template.render(**context))

                try:
                    result = call_api(rendered_url,
                                      intent.apiDetails.requestType, headers,
                                      parameters, isJson)
                except Exception as e:
                    app.logger.warn("API call failed", e)
                    result_json["speechResponse"] = ["Service is not available. Please try again later."]
                else:
                    context["result"] = result
                    template = Template(
                        intent.speechResponse, undefined=SilentUndefined)
                    result_json["speechResponse"] = split_sentence(template.render(**context))
            else:
                context["result"] = {}
                template = Template(intent.speechResponse,
                                    undefined=SilentUndefined)
                result_json["speechResponse"] = split_sentence(template.render(**context))

            #get seat map with updated seats
            print("----result json before treating", result_json)
            result = treat_intent(intent_id, result_json["extractedParameters"], seat_map)
            
            if result is not None:
                result_seat_map, response = result
                result_json["seat_map"] = result_seat_map
                template = Template(response, undefined = SilentUndefined)
                result_json["speechResponse"] = split_sentence(template.render(**context))
            

        app.logger.info(request_json.get("input"), extra=result_json)
        return build_response.build_json(result_json)
    else:
        return abort(400)
        
def update_model(app, message, **extra):
    """
    Signal hook to be called after training is completed.
    Reloads ml models and synonyms.
    :param app:
    :param message:
    :param extra:
    :return:
    """
    global sentence_classifier

    sentence_classifier = EmbeddingIntentClassifier.load(
        app.config["MODELS_DIR"], app.config["USE_WORD_VECTORS"])

    synonyms = get_synonyms()

    global entity_extraction

    entity_extraction = EntityExtractor(synonyms)

    app.logger.info("Intent Model updated")


with app.app_context():
    update_model(app, "Models updated")

model_updated_signal.connect(update_model, app)


def predict(sentence):
    """
    Predict Intent using Intent classifier
    :param sentence:
    :return:
    """
    bot = Bot.objects.get(name="default")
    predicted, intents = sentence_classifier.process(sentence)
    app.logger.info("predicted intent %s", predicted)
    if predicted["confidence"] < bot.config.get("confidence_threshold", .90):
        intents = Intent.objects(intentId=app.config["DEFAULT_FALLBACK_INTENT_NAME"])
        intents = intents.first().intentId
        return intents, 1.0, []
    else:
        return predicted["intent"], predicted["confidence"], intents[1:]
