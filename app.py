import os
import json
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flaskext.mysql import MySQL
from flask_mail import Mail, Message
from controllerDB import ControllerDB
from dotenv import load_dotenv
from datetime import datetime
from clases.admin import Admin
from clases.unit import Unit
from clases import reports


load_dotenv()
folder = os.path.join('fotos') # Referencia a la carpeta

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config['MYSQL_DATABASE_HOST'] = os.getenv("DB_HOST") # Configuración de host DB
app.config['MYSQL_DATABASE_USER'] = os.getenv("DB_USER") # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv("DB_PASSWORD") # Contraseña DB
app.config['MYSQL_DATABASE_PORT'] = int(os.getenv("DB_PORT")) # Puerto DB
app.config['MYSQL_DATABASE_DB']= os.getenv("DB_NAME") # Nombre DB
app.config['JWT_SECRET_KEY']= os.getenv("JWT_SECRET_KEY") # Clave para JWT

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 465  # o 587
app.config['MAIL_USE_TLS'] = False # Cambiar a True si usas el puerto 587
app.config['MAIL_USE_SSL'] = True # Usar SSL en el puerto 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

db = MySQL()
db.init_app(app) # Inicialización de SQL
DB = ControllerDB(db)
jtw =  JWTManager(app)
CORS(app, origins=[os.getenv("URL_FRONT")])
CORS(app, resources={r"/api/terceros/*": {"origins": ["*"]}})

@app.route("/")
def index():
    with open('resources/info_routes.json', 'r') as f:
        data = json.load(f)  # Cargar el JSON del archivo
    return jsonify(data)



@app.route("/login", methods = ['POST'])
def login():
    data = request.get_json()  # Obtiene el JSON de la solicitud

    # Verifica que se haya enviado el JSON
    if not data:
        return jsonify({"error": "No se proporcionó JSON"}), 400

    # Obtiene el nombre de usuario y la contraseña
    username = data.get("username", None)  # Usa .get() para evitar KeyError
    password = data.get("password", None)

    # Verifica que se hayan proporcionado ambos campos
    if not username or not password:
        return jsonify({"error": "Faltan username o password"}), 400
    
    admin = Admin(DB, username, password)
    admin.authenticate()
    if admin.authenticated:
        #  Incluye información del usuario que necesites en la identidad del token
        userIdentity = {"superUser": admin.superUser, "username": admin.username}
        accessToken = create_access_token(identity=userIdentity)  # Crea el token
        return jsonify(access_token=accessToken), 200  # Devuelve el token en la respuesta
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401  # Devuelve error si la autenticación falla
       


@app.route("/crearAdmin", methods =['POST'])
@jwt_required()
def crearAdmin():
    userIdentity = get_jwt_identity()
    if userIdentity.get("superUser",False):
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionó JSON"}), 400
        username = data.get("username", None)  # Usa .get() para evitar KeyError
        password = data.get("password", None)
        superUser = data.get("superUser", False)
        if not username or not password:
            return jsonify({"error": "Faltan username o password"}), 400
        newAdmin = Admin(DB, username, password, superUser)
        mensaje = newAdmin.save()
        return jsonify({"mensaje": mensaje}), 200
    return jsonify({"error":"Administrador sin permisos."})


@app.route("/verAdmins")
@jwt_required()
def verAdmins():
    userIdentity = get_jwt_identity()
    if userIdentity.get("superUser",False):
        admins = DB.auxVerAdmins()
        admins_dict = {}
        for admin in admins:
            admins_dict[admin[1]] = {"id":admin[0], "username": admin[1]}
        return jsonify(admins_dict)


@app.route("/creaUnidad", methods = ['POST'])
@jwt_required()
def createUnit():
    data = request.get_json()
    unit = Unit(data.get("rooms", False), data.get("beds", False), data.get("description", False), data.get("price", False), data.get("amenities", False), data.get("urls_fotos", False), DB)
    result = unit.save()
    return jsonify(result)


@app.route("/eliminarUnidad", methods = ['POST'])
@jwt_required()
def deleteUnit():
    id = request.get_json().get("id",None)
    message = "{'message' : 'Parametro id no encontrado'}"
    if id:
        message = DB.deleteUnit(id)
    return message

@app.route("/api/terceros/units", methods=["GET", "POST"])
def units():
    if request.method == "GET":
        return jsonify(DB.searchUnits())
    elif request.method == "POST":
        criteria = request.get_json()
        return jsonify(DB.searchUnits(criteria))


@app.route("/informes")
@jwt_required()
def generateReports():
    message = {}
    recipient = get_jwt_identity().get("username")
    # recipient = "guillermo.fullstack@gmail.com"
    message = reports.sendReports(app, mail,recipient,DB)
    # for recipient in ["guillermo.fullstack@gmail.com","carol.ceron801@gmail.com","germangp62@gmail.com","msoledadm88@gmail.com"]:
    #     message[recipient] = reports.sendReports(app, mail,recipient,DB)
    return message


if __name__ == "__main__":
     app.run(debug=True, host="localhost", port=5001)