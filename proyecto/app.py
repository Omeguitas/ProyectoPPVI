import os
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flaskext.mysql import MySQL
from controllerDB import controllerDB
from dotenv import load_dotenv
from datetime import datetime
from clases.admin import Admin


load_dotenv()
folder = os.path.join('fotos') # Referencia a la carpeta

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config['MYSQL_DATABASE_HOST'] = os.getenv("DB_HOST") # Configuración de host DB
app.config['MYSQL_DATABASE_USER'] = os.getenv("DB_USER") # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv("DB_PASSWORD") # Contraseña DB
app.config['MYSQL_DATABASE_PORT'] = int(os.getenv("DB_PORT")) # Contraseña DB
app.config['MYSQL_DATABASE_DB']= os.getenv("DB_NAME")
app.config['JWT_SECRET_KEY']= os.getenv("JWT_SECRET_KEY")
app.config['FOLDER'] = folder # Indicamos que vamos a guardar esta ruta de la carpeta

db = MySQL()
db.init_app(app) # Inicialización de SQL
DB = controllerDB(db)
jtw =  JWTManager(app)
CORS(app, origins=[os.getenv("URL_FRONT")])
CORS(app, resources={r"/api/terceros/*": {"origins": ["*"]}})

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
def crearSuperadmin():
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



if __name__ == "__main__":
     app.run(debug=True, host="localhost", port=5001)












'''
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS # Importa CORS

app = Flask(__name__)
CORS(app) # Habilita CORS para todas las rutas

# Configuración de la clave secreta. ¡CAMBIAR ESTO EN PRODUCCIÓN!
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # ¡No uses esto en producción!
jwt = JWTManager(app)

# Ruta para el inicio de sesión y generación del token
@app.route("/login", methods=["POST"])
def login():
    """
    Esta ruta recibe un JSON con 'username' y 'password',
    verifica las credenciales (simulado), y devuelve un token JWT.
    """
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

    # *** Aquí iría la lógica de autenticación REAL (verificar en la base de datos) ***
    # Simulando una autenticación exitosa para el usuario "test" y contraseña "password"
    if username == "test" and password == "password":
        # En una aplicación real, obtendrías el ID del usuario de la base de datos.
        user_id = 123
        #  Incluye información del usuario que necesites en la identidad del token
        identidad_usuario = {"user_id": user_id, "username": username}
        access_token = create_access_token(identity=identidad_usuario)  # Crea el token
        return jsonify(access_token=access_token), 200  # Devuelve el token en la respuesta
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401  # Devuelve error si la autenticación falla

# Ruta protegida que requiere un token válido
@app.route("/protegido", methods=["GET"])
@jwt_required()  # Decorador que protege la ruta
def protegido():
    """
    Esta ruta solo es accesible con un token JWT válido.
    Devuelve la identidad del usuario obtenida del token.
    """
    identidad_usuario = get_jwt_identity()  # Obtiene la información del usuario del token
    return jsonify(logged_in_as=identidad_usuario), 200  # Devuelve la identidad del usuario como JSON

if __name__ == "__main__":
    app.run(debug=True)  # No usar debug=True en producción
'''