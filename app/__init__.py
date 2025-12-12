from flask import Flask
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    app_key=os.environ.get("APP_SECRET_KEY")
    app.config["SECRET_KEY"] = app_key

    from .routes import main
    app.register_blueprint(main)

    return app