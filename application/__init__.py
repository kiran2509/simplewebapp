from flask import Flask
from flask_mongoengine import MongoEngine 
from application.config import Config
from flask_login import LoginManager

app=Flask(__name__)
app.config.from_object(Config)

db=MongoEngine()
db.init_app(app)

login_manager=LoginManager()
login_manager.login_view="login"
login_manager.init_app(app)


from application import routes