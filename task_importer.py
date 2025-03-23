from datetime import datetime
from models import Task, db

def import_tasks_from_txt(file_path):
    """Importa tareas desde archivo TXT"""
    tasks = []
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    date_str, description, phone = line.strip().split(';')
                    due_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    task = Task(
                        description=description,
                        due_date=due_date,
                        phone=phone
                    )
                    tasks.append(task)
                except ValueError as e:
                    errors.append(f"Error en línea {line_num}: {str(e)}")
                    continue
        
        if tasks:
            db.session.bulk_save_objects(tasks)
            db.session.commit()
            
        return len(tasks), errors
    except Exception as e:
        return 0, [f"Error al procesar archivo: {str(e)}"]
