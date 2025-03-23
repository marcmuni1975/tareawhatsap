# Task Manager con Recordatorios WhatsApp

Aplicación Flask para gestionar tareas con recordatorios automáticos vía WhatsApp Business.

## Características

- Registro de tareas con fechas
- Importación masiva desde archivo TXT
- Recordatorios automáticos vía WhatsApp (7 y 3 días antes)
- Base de datos SQLite

## Configuración

1. Copia `.env.example` a `.env`
2. Configura tus credenciales de CallMeBot y número de teléfono
3. Instala dependencias: `pip install -r requirements.txt`
4. Inicia la aplicación: `python app.py`

## Formato del archivo TXT para importación

```
fecha;descripción;teléfono
2025-04-01;Reunión importante;+1234567890
```

## Despliegue en Railway

1. Conecta tu repositorio de GitHub
2. Configura las variables de entorno
3. ¡Listo! Railway detectará automáticamente la configuración
