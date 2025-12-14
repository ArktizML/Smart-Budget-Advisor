from flask import Flask
import os
from dotenv import load_dotenv
from ai import ai
from .routes import main 

def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    app_key=os.environ.get("APP_SECRET_KEY")
    app.config["SECRET_KEY"] = app_key

    
    app.register_blueprint(main)
    app.register_blueprint(ai)
    app.register_blueprint(app)

    return app