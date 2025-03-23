from app import app, db
from models import User, Task
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        # Crear usuario maestro si no existe
        master_user = User.query.filter_by(is_master=True).first()
        if not master_user:
            master_user = User(username='admin', is_master=True)
            master_user.set_password('adminpass123')
            db.session.add(master_user)
            db.session.commit()
            print("Usuario maestro creado")
        else:
            print("Usuario maestro ya existe")
        
        # Agregar columna created_by si no existe
        try:
            db.session.execute(text('ALTER TABLE task ADD COLUMN created_by INTEGER REFERENCES user(id)'))
            db.session.commit()
            print("Columna created_by agregada")
        except Exception as e:
            print(f"La columna ya existe o hubo un error: {e}")
            db.session.rollback()
        
        # Asignar todas las tareas existentes al usuario maestro
        try:
            db.session.execute(text('UPDATE task SET created_by = :user_id WHERE created_by IS NULL'), {'user_id': master_user.id})
            db.session.commit()
            print("Tareas existentes asignadas al usuario maestro")
        except Exception as e:
            print(f"Error al actualizar tareas: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database()
