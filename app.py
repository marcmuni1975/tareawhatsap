from flask import Flask, render_template, request, flash, redirect, url_for, session
from datetime import datetime
from models import db, Task, User
from config import Config
from scheduler import init_scheduler
from auth import login_required, master_required
import os

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))

# Configurar el host y puerto para Railway
port = int(os.getenv('PORT', 8080))
host = '0.0.0.0'  # Necesario para Railway

db.init_app(app)

with app.app_context():
    db.create_all()
    # Crear usuario maestro por defecto si no existe
    User.create_master_user('admin', 'adminpass123')
    scheduler = init_scheduler(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión', 'success')
    return redirect(url_for('login'))

@app.route('/users')
@master_required
def list_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['POST'])
@master_required
def add_user():
    try:
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('list_users'))
        
        user = User(username=username, created_by=session['user_id'])
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al crear usuario: {str(e)}', 'error')
    return redirect(url_for('list_users'))

@app.route('/users/delete/<int:user_id>')
@master_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('No puedes eliminar tu propio usuario', 'error')
        return redirect(url_for('list_users'))
    
    user = User.query.get_or_404(user_id)
    if user.is_master:
        flash('No se puede eliminar el usuario maestro', 'error')
        return redirect(url_for('list_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    return redirect(url_for('list_users'))

@app.route('/')
@login_required
def index():
    # Obtener parámetros de búsqueda
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    
    # Construir la consulta base
    query = Task.query.filter_by(created_by=session['user_id'])
    
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
@login_required
def add_task():
    try:
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        task = Task(
            description=request.form['description'],
            due_date=due_date,
            phone=Config.PHONE_NUMBER,
            created_by=session['user_id']
        )
        db.session.add(task)
        db.session.commit()
        flash('Tarea agregada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al agregar tarea: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/task/edit/<int:task_id>', methods=['POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.created_by != session['user_id']:
        flash('No tienes permiso para editar esta tarea', 'error')
        return redirect(url_for('index'))
    
    try:
        task.description = request.form['description']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        db.session.commit()
        flash('Tarea actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar tarea: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/task/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.created_by != session['user_id']:
        flash('No tienes permiso para eliminar esta tarea', 'error')
        return redirect(url_for('index'))
    
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
@login_required
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
                        phone=Config.PHONE_NUMBER,
                        created_by=session['user_id']
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
@login_required
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
    app.run(host=host, port=port, debug=False)
