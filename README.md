🎓 GC ACADEMIA — Plataforma de Tutoría Mágica
Una plataforma educativa con diseño Harry Potter y funcionalidad en tiempo real
✨ “La magia está en el aprendizaje… y en el código.”

📂 Estructura del Proyecto

gc_academia/
├── app.py                     # Entrada principal (Flask)
├── requirements.txt           # Dependencias
├── static/
│   ├── css/
│   │   └── style.css        # Estilos globales (parchment, Hogwarts, etc.)
│   ├── js/
│   │   ├── emoji-data.js    # Emojis PNG personalizados (dragon.png, lechuza.png, etc.)
│   │   └── chat.js          # Lógica del chat en vivo
│   └── emojis/                # 🖼️ Tus PNGs: dragon.png, dumbledore.png, harry.png, ...
├── templates/
│   ├── base.html            # Layout base (header, footer, estilos mágicos)
│   ├── index.html
│   ├── profesor/
│   │   ├── catalogo.html
│   │   ├── horario.html     # Agendar tutorías
│   │   └── chat_vivo.html   # Chat profesor (✅ ya corregido)
│   └── alumno/
│       └── chat_vivo.html   # Chat alumno (✅ ya corregido)
├── models.py                # Modelos SQLAlchemy (User, Curso, Horario, Mensaje, etc.)
├── .env                     # 🔒 Variables de entorno (NO subir a Git)
└── .gitignore

🚀 Cómo Arrancar en Local
1. Clona el repositorio

git clone https://github.com/tu-usuario/gc-academia.git
cd gc-academia

2. Crea un entorno virtual e instala dependencias

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

3. Configura la base de datos PostgreSQL

A. Crea un archivo .env en la raíz del proyecto:

# .env
DATABASE_URL=postgresql://postgres:123456@localhost:5432/formacion_web
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura

B. Instala PostgreSQL (si no lo tienes):
Windows: PostgreSQL Installer
macOS: brew install postgresql
Linux: sudo apt install postgresql postgresql-contrib

C. Crea la base de datos y usuario:

-- En psql o pgAdmin
CREATE DATABASE inmogcyc;
CREATE USER postgres WITH PASSWORD '123456';
GRANT ALL PRIVILEGES ON DATABASE formacion_web TO postgres;

4. Crea las tablas en PostgreSQL

Ejecuta este script una vez:

# create_db.py
from models import db, app

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas en PostgreSQL: formacion_web")

    python create_db.py

    5. Ejecuta la aplicación

    flask run --host=0.0.0.0 --port=5000

     Accede en tu navegador: [http://localhost:5000]

     🗃️ Modelo de Base de Datos (PostgreSQL)
Diagrama de Entidades y Relaciones

+----------------+       +----------------+       +----------------+
|     users      |       |     cursos     |       |  curso_profesor|
+----------------+       +----------------+       +----------------+
| id (PK)        |<----->| id (PK)        |<----->| curso_id (FK)  |
| username       |       | nombre         |       | profesor_id(FK)|
| email          |       | descripcion    |       +----------------+
| password_hash  |       | fecha_inicio   |
| role           |       | fecha_fin      |
+----------------+       +----------------+

+----------------+       +----------------+       +----------------+
|   inscripciones|       |    horarios    |       |   mensajes     |
+----------------+       +----------------+       +----------------+
| id (PK)        |       | id (PK)        |       | id (PK)        |
| alumno_id (FK) |<----->| curso_id (FK)  |<----->| remitente_id(FK)|
| curso_id (FK)  |       | profesor_id(FK)|       | curso_id (FK)  |
| fecha_inscripcion|     | fecha_hora     |       | contenido      |
| estado         |       | duracion_minutos|       | fecha          |
+----------------+       +----------------+       +----------------+

+----------------+       +----------------+
|    soporte     |       |     pagos      |
+----------------+       +----------------+
| id (PK)        |       | id (PK)        |
| remitente_id(FK)|     | alumno_id (FK) |
| mensaje_texto  |       | curso_id (FK)  |
| fecha          |       | monto          |
| leido          |       | metodo         |
| respuesta_texto|       | fecha_pago     |
| fecha_respuesta|       +----------------+
| resuelto       |
+----------------+

🔑 Tipos de datos PostgreSQL:
id: SERIAL PRIMARY KEY
username, email, role: VARCHAR(255)
password_hash: TEXT
fecha_hora, fecha: TIMESTAMP
monto: NUMERIC(10,2)
estado, metodo: VARCHAR(50)

🛠️ Cómo Crear la Base de Datos en PostgreSQL
Paso 1: Conéctate a PostgreSQL

psql -U postgres -h localhost

Paso 2: Ejecuta estos comandos SQL
sql

-- Crear base de datos
CREATE DATABASE inmogcyc;

-- Conectarse a la base de datos
\c inmogcyc

-- Crear tablas
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'alumno'
);

CREATE TABLE cursos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE
);

CREATE TABLE curso_profesor (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    profesor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(curso_id, profesor_id)
);

CREATE TABLE inscripciones (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'activa'
);

CREATE TABLE horarios (
    id SERIAL PRIMARY KEY,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    profesor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fecha_hora TIMESTAMP NOT NULL,
    duracion_minutos INTEGER DEFAULT 60
);

CREATE TABLE mensajes (
    id SERIAL PRIMARY KEY,
    remitente_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    contenido TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE soporte (
    id SERIAL PRIMARY KEY,
    remitente_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    mensaje_texto TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leido BOOLEAN DEFAULT FALSE,
    respuesta_texto TEXT,
    fecha_respuesta TIMESTAMP,
    resuelto BOOLEAN DEFAULT FALSE
);

CREATE TABLE pagos (
    id SERIAL PRIMARY KEY,
    alumno_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    curso_id INTEGER NOT NULL REFERENCES cursos(id) ON DELETE CASCADE,
    monto NUMERIC(10,2) NOT NULL,
    metodo VARCHAR(50),
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Paso 3: Verifica la conexión en tu app.py

# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

🧠 Cómo Funciona la Web
(Mismo contenido que antes, pero ahora con PostgreSQL como backend)
🌐 Flujo Principal:
Inicio → Login/Registro (/login, /register)
Profesor:

Ve su catálogo de cursos (/profesor/catalogo)
Agenda horarios (/profesor/horario/<curso_id>)
Chatea en vivo con alumnos (/profesor/chat/<curso_id>)

Alumno:

Se inscribe en cursos
Ve sus horarios y tutorías programadas
Chatea en vivo con su profesor (/alumno/chat/<curso_id>)
💬 Chat en Vivo (funcionalidad clave)
Usa Socket.IO para comunicación en tiempo real
Mensajes se guardan en tabla mensajes (PostgreSQL)
Emojis personalizados: PNGs en /static/emojis/ → insertados como <img src="...">
Diseño mágico: pergamino, gradientes, efectos de brillo

📦 Dependencias (requirements.txt)

Flask==2.3.3
Flask-SocketIO==5.3.3
Flask-SQLAlchemy==3.0.5
psycopg2-binary==2.9.7      # ¡Driver PostgreSQL!
python-dotenv==1.0.0
eventlet==0.33.3

