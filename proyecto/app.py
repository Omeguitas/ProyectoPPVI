import os
from flask import Flask
from flaskext.mysql import MySQL




app = Flask(__name__)
app.secret_key="Omeguitas"
db = MySQL()
app.config['MYSQL_DATABASE_HOST']="localhost" # Configuración de host DB
app.config['MYSQL_DATABASE_USER']='root' # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD']='' # Contraseña DB
app.config['MYSQL_DATABASE_DB']='my_database'

db.init_app(app) # Inicialización de SQL
folder = os.path.join('fotos') # Referencia a la carpeta
app.config['FOLDER'] = folder # Indicamos que vamos a guardar esta ruta de la carpeta
