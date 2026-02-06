from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "dev-secret-key-no-usar-en-produccion"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123456@localhost/formacion_web_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
