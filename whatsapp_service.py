import requests
import urllib.parse
from config import Config

def send_whatsapp_message(phone, message):
    """
    Envía un mensaje de WhatsApp usando CallMeBot API
    """
    try:
        encoded_message = urllib.parse.quote(message)
        api_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={Config.CALLMEBOT_APIKEY}"
        print(f"URL de la API: {api_url}")
        
        response = requests.get(api_url)
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta completa: {response.text}\n")
        
        # CallMeBot devuelve 200 para éxito y otros códigos para errores
        return response.status_code == 200
    except Exception as e:
        print(f"Error al enviar mensaje: {str(e)}")
        return False

def create_reminder_message(task, days):
    """Crea mensaje de recordatorio"""
    return f" Recordatorio: '{task.description}' vence en {days} días (fecha: {task.due_date.strftime('%Y-%m-%d')})"
