import os

class Config(object):
    DEBUG = False
    MONGODB_DB = "heroku_nl4m3cv8"
    MONGODB_HOST = "ds253017.mlab.com"
    MONGODB_PORT = 53017
    MONGODB_USERNAME = "heroku_nl4m3cv8"
    MONGODB_USERNAME = "mpu4itfan5g0kbh3605phbjeah"

    # Intent Classifier model details
    MODELS_DIR = "model_files/"
    INTENT_MODEL_NAME = "intent.model"
    DEFAULT_FALLBACK_INTENT_NAME = "fallback"
    DEFAULT_WELCOME_INTENT_NAME = "init_conversation"
    USE_WORD_VECTORS = True


class Development(Config):
    DEBUG = True


class Production(Config):
    # MongoDB Database Details
    #MONGODB_DB = os.environ.get("MONGODB_URI")
    MONGODB_SETTINGS = {
        "host": os.environ.get("MONGODB_URI"),
    }

    # Web Server details
    WEB_SERVER_PORT = 8001
