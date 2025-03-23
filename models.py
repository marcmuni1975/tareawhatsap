from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    reminder_7_sent = db.Column(db.Boolean, default=False)
    reminder_3_sent = db.Column(db.Boolean, default=False)
    last_reminder_sent = db.Column(db.DateTime, nullable=True)  # Último recordatorio enviado
    is_confirmed = db.Column(db.Boolean, default=False)  # Si la tarea fue confirmada
    confirmation_code = db.Column(db.String(10), nullable=True)  # Código de confirmación
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Task {self.description}>'
