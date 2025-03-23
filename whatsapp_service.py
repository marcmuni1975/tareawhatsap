import urllib.parse
import requests
from config import Config
from datetime import datetime

def get_task_emoji(description):
    """Determina el emoji apropiado basado en el contenido de la tarea"""
    description = description.lower()
    
    # Categorías comunes y sus emojis
    categories = {
        'reunión': '👥',
        'reunion': '👥',
        'meet': '👥',
        'llamada': '📞',
        'llamar': '📞',
        'email': '📧',
        'correo': '📧',
        'mail': '📧',
        'documento': '📄',
        'informe': '📊',
        'reporte': '📊',
        'presentación': '🎯',
        'presentacion': '🎯',
        'pago': '💰',
        'factura': '💰',
        'comprar': '🛒',
        'compra': '🛒',
        'médico': '👨‍⚕️',
        'medico': '👨‍⚕️',
        'doctor': '👨‍⚕️',
        'hospital': '🏥',
        'estudiar': '📚',
        'examen': '📝',
        'tarea': '📚',
        'proyecto': '💻',
        'deadline': '⚠️',
        'urgente': '🚨',
        'importante': '❗',
        'recordar': '🔔',
        'recordatorio': '🔔',
        'cumpleaños': '🎂',
        'cumpleanos': '🎂',
        'fiesta': '🎉',
        'viaje': '✈️',
        'vacaciones': '🌴',
        'ejercicio': '💪',
        'gym': '🏋️',
        'deporte': '⚽',
    }
    
    # Buscar categorías en la descripción
    for keyword, emoji in categories.items():
        if keyword in description:
            return emoji
    
    return '📌'  # Emoji por defecto si no hay coincidencias

def get_urgency_prefix(days_left):
    """Determina el prefijo de urgencia basado en los días restantes"""
    if days_left == 0:
        return '🚨 ÚLTIMO DÍA'
    elif days_left < 0:
        return '⚠️ ATRASADO'
    elif days_left <= 1:
        return '❗ URGENTE'
    elif days_left <= 3:
        return '⚡ PRÓXIMO'
    else:
        return '🔔 Recordatorio'

def create_reminder_message(task, days_left):
    """Crea un mensaje de recordatorio personalizado"""
    task_emoji = get_task_emoji(task.description)
    urgency_prefix = get_urgency_prefix(days_left)
    
    # Mensaje base
    message = f"{urgency_prefix}: {task_emoji} {task.description}"
    
    # Agregar información de fecha
    if days_left == 0:
        message += " - ¡VENCE HOY!"
    elif days_left < 0:
        message += f" - Venció hace {abs(days_left)} días"
    elif days_left == 1:
        message += " - Vence MAÑANA"
    else:
        message += f" - Vence en {days_left} días"
    
    # Agregar código de confirmación
    message += f"\n\nPara confirmar, responde: OK {task.confirmation_code}"
    
    # Agregar mensaje motivacional para tareas urgentes
    if days_left <= 1:
        message += "\n\n💪 ¡Tú puedes lograrlo! No dejes para mañana lo que puedes hacer hoy."
    
    return message

def send_whatsapp_message(phone, message):
    """Envía un mensaje de WhatsApp usando CallMeBot"""
    try:
        encoded_message = urllib.parse.quote(message)
        api_url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={Config.CALLMEBOT_APIKEY}"
        
        print(f"URL de la API: {api_url}")
        response = requests.get(api_url)
        print(f"Código de estado: {response.status_code}")
        print(f"Respuesta completa: {response.text}\n")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error al enviar mensaje: {str(e)}")
        return False
