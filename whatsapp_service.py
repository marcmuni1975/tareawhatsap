import requests
from config import Config
import urllib.parse

def send_whatsapp_message(phone, message):
    """Envía mensaje de WhatsApp usando CallMeBot API"""
    # Codificar el mensaje para la URL
    encoded_message = urllib.parse.quote(message)
    
    api_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={Config.CALLMEBOT_APIKEY}"
    try:
        print(f"URL de la API: {api_url}")  # Debug - URL completa
        response = requests.get(api_url)
        print(f"Código de estado: {response.status_code}")  # Debug - Código de estado
        print(f"Respuesta completa: {response.text}")  # Debug - Respuesta completa
        
        if response.status_code == 200:
            if "Message queued" in response.text:
                return True
            else:
                print(f"Error en la respuesta: {response.text}")
                return False
        return False
    except Exception as e:
        print(f"Error enviando mensaje WhatsApp: {e}")
        return False

def create_reminder_message(task, days):
    """Crea mensaje de recordatorio"""
    return f"🔔 Recordatorio: '{task.description}' vence en {days} días (fecha: {task.due_date.strftime('%Y-%m-%d')})"
