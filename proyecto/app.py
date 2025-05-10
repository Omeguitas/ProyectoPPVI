import os
from flask import Flask
from flaskext.mysql import MySQL
import controllerDB as DB
from dotenv import load_dotenv
from datetime import datetime

database = 'alojamientosomeguitas_particles'
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
# app.secret_key = os.getenv("SECRET_KEY")
db = MySQL()
app.config['MYSQL_DATABASE_HOST'] = os.getenv("DB_HOST") # Configuración de host DB
app.config['MYSQL_DATABASE_USER'] = os.getenv("DB_USER") # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv("DB_PASSWORD") # Contraseña DB
app.config['MYSQL_DATABASE_PORT'] = int(os.getenv("DB_PORT")) # Contraseña DB
db.init_app(app) # Inicialización de SQL
# DB.createDB(db, database)
app.config['MYSQL_DATABASE_DB']= os.getenv("DB_NAME")

folder = os.path.join('fotos') # Referencia a la carpeta
app.config['FOLDER'] = folder # Indicamos que vamos a guardar esta ruta de la carpeta

# DB.initDB(db)

inicio = datetime(2025,6,12)
fin = datetime(2025,7,12)
print(DB.searchUnits({"start_date": inicio, "end_date": fin, "beds": 3}, db))