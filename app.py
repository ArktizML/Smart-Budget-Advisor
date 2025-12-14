from app import create_app
import logging, os
from dotenv import load_dotenv
from groq import Groq
from logging.handlers import RotatingFileHandler

load_dotenv()
app_key=os.environ.get("APP_SECRET_KEY")
app = create_app()
app.secret_key = app_key
app.config['DEBUG'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

handler = RotatingFileHandler('logs/error.log', maxBytes=1000000, backupCount=3)
handler.setLevel(logging.WARNING)
app.logger.addHandler(handler)


api_key=os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

if __name__ == "__main__":
    app.run(debug=True)