import os
from dotenv import load_dotenv
from pathlib import Path

# Encontrar el archivo .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"Advertencia: No se encontró el archivo .env en {env_path}")

class Config:
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de CallMeBot - usar valores por defecto si no están en .env
    CALLMEBOT_APIKEY = os.getenv('CALLMEBOT_APIKEY', '6171027')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER', '+56978475180')
    
    def __init__(self):
        # Validar que los valores requeridos estén presentes y tengan el formato correcto
        if not self.CALLMEBOT_APIKEY or len(self.CALLMEBOT_APIKEY.strip()) == 0:
            print("Advertencia: CALLMEBOT_APIKEY no está configurado, usando valor por defecto")
        
        if not self.PHONE_NUMBER or not self.PHONE_NUMBER.startswith('+'):
            print("Advertencia: PHONE_NUMBER debe comenzar con '+' y tener formato internacional")
