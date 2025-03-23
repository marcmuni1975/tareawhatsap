from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from models import db, Task
from config import Config
from scheduler import init_scheduler
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.urandom(24)

db.init_app(app)

with app.app_context():
    db.create_all()
    scheduler = init_scheduler()

@app.route('/')
def index():
    # Obtener parámetros de búsqueda
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    
    # Construir la consulta base
    query = Task.query
    
    # Aplicar filtros de búsqueda
    if search:
        query = query.filter(Task.description.ilike(f'%{search}%'))
    
    if status == 'pending':
        query = query.filter_by(is_confirmed=False)
    elif status == 'confirmed':
        query = query.filter_by(is_confirmed=True)
    
    # Ordenar por fecha
    tasks = query.order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks)

@app.route('/task/add', methods=['POST'])
def add_task():
    try:
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task = Task(
            description=request.form['description'],
            due_date=due_date,
            phone=Config.PHONE_NUMBER  # Usar el número configurado por defecto
        )
        db.session.add(task)
        db.session.commit()
        flash('Tarea agregada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al agregar tarea: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/task/edit/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Tarea actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar tarea: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/task/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar tarea: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/confirm/<code>')
def confirm_task(code):
    task = Task.query.filter_by(confirmation_code=code).first()
    if task:
        task.is_confirmed = True
        db.session.commit()
        return "Tarea confirmada exitosamente. Ya no recibirás más recordatorios para esta tarea."
    return "Código de confirmación no válido."

@app.route('/task/import', methods=['POST'])
def import_tasks():
    if 'file' not in request.files:
        flash('No se seleccionó archivo', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó archivo', 'error')
        return redirect(url_for('index'))
    
    if not file.filename.endswith('.txt'):
        flash('El archivo debe ser .txt', 'error')
        return redirect(url_for('index'))
    
    # Guardar archivo temporalmente
    temp_path = 'temp_tasks.txt'
    file.save(temp_path)
    
    try:
        tasks_added = 0
        with open(temp_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    date_str, description = line.strip().split(';')
                    due_date = datetime.strptime(date_str, '%Y-%m-%d')
                    task = Task(
                        description=description,
                        due_date=due_date,
                        phone=Config.PHONE_NUMBER  # Usar el número configurado por defecto
                    )
                    db.session.add(task)
                    tasks_added += 1
                except ValueError as e:
                    flash(f'Error en línea: {line.strip()} - {str(e)}', 'error')
        
        if tasks_added > 0:
            db.session.commit()
            flash(f'Se importaron {tasks_added} tareas exitosamente', 'success')
    except Exception as e:
        flash(f'Error al importar tareas: {str(e)}', 'error')
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return redirect(url_for('index'))

@app.route('/test_whatsapp')
def test_whatsapp():
    try:
        from whatsapp_service import send_whatsapp_message
        phone = Config.PHONE_NUMBER
        success = send_whatsapp_message(phone, " Prueba de sistema de tareas - Mensaje de prueba")
        if success:
            return f"Mensaje enviado correctamente a {phone}"
        return f"Error al enviar el mensaje. Configuración actual: Phone={phone}, API Key={Config.CALLMEBOT_APIKEY}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
