import os

class Config():
    # SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1234@localhost:3306/smart_room"
    SECRET_KEY = "bsme2022"
    SQLALCHEMY_TRACK_MODIFICATION = True
    


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig 
}