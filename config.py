import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CALLMEBOT_APIKEY = os.getenv('CALLMEBOT_APIKEY')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
