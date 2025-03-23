from datetime import datetime, timedelta
import random
import string
from apscheduler.schedulers.background import BackgroundScheduler
from models import Task, db
from whatsapp_service import send_whatsapp_message

def generate_confirmation_code():
    """Genera un código de confirmación aleatorio"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_check_reminders_job(app):
    """Crea una función de verificación de recordatorios con el contexto de la aplicación"""
    def check_and_send_reminders():
        with app.app_context():
            now = datetime.utcnow()
            print(f"Verificando recordatorios en: {now}")
            
            # Recordatorios de 7 días
            tasks_7_days = Task.query.filter(
                Task.due_date <= now + timedelta(days=7),
                Task.due_date > now + timedelta(days=6),
                Task.reminder_7_sent == False
            ).all()
            
            print(f"Encontradas {len(tasks_7_days)} tareas para recordatorio de 7 días")
            for task in tasks_7_days:
                if not task.confirmation_code:
                    task.confirmation_code = generate_confirmation_code()
                message = f"🔔 Recordatorio (7 días): {task.description} vence el {task.due_date.strftime('%Y-%m-%d')}. Para confirmar, responde: OK {task.confirmation_code}"
                print(f"Enviando recordatorio 7 días para: {task.description}")
                if send_whatsapp_message(task.phone, message):
                    task.reminder_7_sent = True
                    task.last_reminder_sent = now
                    print("Recordatorio enviado exitosamente")
            
            # Recordatorios de 3 días
            tasks_3_days = Task.query.filter(
                Task.due_date <= now + timedelta(days=3),
                Task.due_date > now + timedelta(days=2),
                Task.reminder_3_sent == False
            ).all()
            
            print(f"Encontradas {len(tasks_3_days)} tareas para recordatorio de 3 días")
            for task in tasks_3_days:
                if not task.confirmation_code:
                    task.confirmation_code = generate_confirmation_code()
                message = f"🔔 Recordatorio (3 días): {task.description} vence el {task.due_date.strftime('%Y-%m-%d')}. Para confirmar, responde: OK {task.confirmation_code}"
                print(f"Enviando recordatorio 3 días para: {task.description}")
                if send_whatsapp_message(task.phone, message):
                    task.reminder_3_sent = True
                    task.last_reminder_sent = now
                    print("Recordatorio enviado exitosamente")
            
            # Recordatorios diarios para tareas no confirmadas
            tasks_daily = Task.query.filter(
                Task.due_date > now,
                Task.is_confirmed == False,
                (Task.last_reminder_sent == None) | 
                (Task.last_reminder_sent <= now - timedelta(hours=12))  # Recordar cada 12 horas
            ).all()
            
            print(f"Encontradas {len(tasks_daily)} tareas para recordatorio diario")
            for task in tasks_daily:
                if not task.confirmation_code:
                    task.confirmation_code = generate_confirmation_code()
                days_left = (task.due_date - now).days
                message = f"⏰ Recordatorio: '{task.description}' vence en {days_left} días. Para dejar de recibir recordatorios, responde: OK {task.confirmation_code}"
                print(f"Enviando recordatorio diario para: {task.description}")
                if send_whatsapp_message(task.phone, message):
                    task.last_reminder_sent = now
                    print("Recordatorio enviado exitosamente")
            
            db.session.commit()
    
    return check_and_send_reminders

def init_scheduler(app):
    """Inicializa el programador de tareas"""
    scheduler = BackgroundScheduler()
    check_reminders_job = create_check_reminders_job(app)
    scheduler.add_job(check_reminders_job, 'interval', minutes=1)
    scheduler.start()
    # Ejecutar una verificación inmediata
    check_reminders_job()
    return scheduler
