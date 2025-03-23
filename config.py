import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de CallMeBot
    CALLMEBOT_APIKEY = os.getenv('CALLMEBOT_APIKEY')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    
    # Asegurarse de que las variables requeridas estén presentes
    if not CALLMEBOT_APIKEY:
        raise ValueError("CALLMEBOT_APIKEY no está configurado en .env")
    if not PHONE_NUMBER:
        raise ValueError("PHONE_NUMBER no está configurado en .env")
