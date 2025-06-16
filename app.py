import os
import json
from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flaskext.mysql import MySQL
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer 
from controllerDB import ControllerDB
from dotenv import load_dotenv
from datetime import datetime as dt, timedelta
from clases.admin import Admin
from clases.unit import Unit
from clases import reports
from clases.guest import Guest
from clases.reservation import Reservation
from clases.reports import sendMail


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
CORS(app, origins=[os.getenv("URL_FRONT")+"/*","*"])
CORS(app, resources={r"/api/terceros/*": {"origins": ["*"]}})

@app.route("/")
def index():
    with open('resources/info_routes.json', 'r') as f:
        data = json.load(f)  # Cargar el JSON del archivo
    return jsonify(data), 200



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
        userIdentity = f'{{"superUser": {json.dumps(admin.superUser)}, "username": {json.dumps(admin.username)}}}'
        accessToken = create_access_token(identity=userIdentity,expires_delta=timedelta(1))  # Crea el token
        return jsonify({"access_token":accessToken, "superUser":admin.superUser}), 200  # Devuelve el token en la respuesta
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401  # Devuelve error si la autenticación falla
       


@app.route("/crearAdmin", methods =['POST'])
@jwt_required()
def crearAdmin():
    userIdentity = json.loads(get_jwt_identity())
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
        return jsonify({"mensaje": mensaje}), 201
    return jsonify({"error":"Administrador sin permisos necesarios."}), 403


@app.route("/verAdmins")
@jwt_required()
def verAdmins():
    userIdentity = json.loads(get_jwt_identity())
    if userIdentity.get("superUser",False):
        admins = DB.auxVerAdmins()
        admins_dict = {}
        for admin in admins:
            admins_dict[admin[1]] = {"id":admin[0], "username": admin[1],"superUser": admin[3]}
        return jsonify(admins_dict), 200
    return jsonify({"error":"Administrador sin permisos necesarios."}), 403
    
    
@app.route("/deleteAdmin/<int:id>", methods = ['DELETE'])
@jwt_required()
def deleteAdmin(id:int):
    userIdentity = json.loads(get_jwt_identity())
    if userIdentity.get("superUser",False):
        if DB.deleteAdmin(id):
            return jsonify({"message":"Administrador borrado con éxito"}), 200
        return jsonify({"message":"Administrador no encontrado"}), 404
    return jsonify({"error":"Administrador sin permisos necesarios."}), 403
    
@app.route("/editPass", methods = ['POST'])
@jwt_required()
def editPass():
    userIdentity = json.loads(get_jwt_identity())
    email = userIdentity.get("username",False)
    password = request.get_json().get("password")
    if DB.modifyPassAdmin(email, password):
        return jsonify({"message":"Contraseña modificada con éxito"}), 200
    return jsonify({"message":"Administrador no encontrado"}), 404

@app.route("/recoveryPass", methods = ['GET','POST'])
def recoveryPass():
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    salt = 'password-reset-salt'
    if request.method == 'GET':
        username = request.args.get("username")
        admin = Admin(DB, username,"","")
        if DB.searchAdmin(admin):
            token = serializer.dumps(username, salt)
            urlFront = os.getenv("URL_FRONT")
            resetLink = f"{urlFront}/recoveryPass?token={token}"
            response, code = reports.sendMail(app,username,"Siga el siguiente link para reestablecer su contraseña",[],render_template("/mails/recoveryPass.html", link=resetLink))
            return jsonify(response), code
        return jsonify({"message":"Si el usuario existe, se enviará un correo electrónico con el link de recuperación."}), 200
    elif request.method == 'POST':
        data = request.get_json()
        token = data.get('token')
        password = data.get('password')
        try:
            email = serializer.loads(token,salt=salt,max_age=900)
            if password and email and DB.modifyPassAdmin(email, password):
                return jsonify({"message":"Contraseña modificada con éxito"}), 200
        except:
            return jsonify({"message":"Administrador no encontrado"}), 404


@app.route("/creaUnidad", methods = ['POST'])
@jwt_required()
def createUnit():
    data = request.get_json()
    unit = Unit(data.get("rooms", False), data.get("beds", False), data.get("description", False), data.get("price", False), data.get("amenities", False), data.get("urls_fotos", False), DB, data.get("title", ""),data.get("bathrooms", 0),data.get("address", ""))
    result = unit.save()
    return jsonify(result), 201
    # TODO respuesta en caso de fallo

@app.route("/editarUnidad", methods = ['POST'])
@jwt_required()
def editUnit():
    data = request.get_json()
    unit = Unit(data.get("rooms", False), data.get("beds", False), data.get("description", False), data.get("price", False), data.get("amenities", False), data.get("urls_fotos", False), DB, data.get("title", ""),data.get("bathrooms", 0),data.get("address", ""), data.get("id"))
    result = unit.edit()
    return jsonify(result), 200
    # TODO respuesta en caso de fallo


@app.route("/eliminarUnidad", methods = ['POST'])
@jwt_required()
def deleteUnit():
    id = request.get_json().get("id",None)
    message, code = {'message' : 'Parametro id no encontrado'}, 404
    if id:
        message, code = DB.deleteUnit(id)
    return jsonify(message), code

@app.route("/api/terceros/units/", methods=["GET", "POST"])
def units():
    id = request.args.get('id')
    if request.method == "GET":
        if id:
            lista = jsonify(DB.searchUnits({"id":id}))
        else:
            lista = jsonify(DB.searchUnits()) 
        if lista:
            code = 200
        else:
            code = 404
        return lista, code
    elif request.method == "POST":
        criteria = request.get_json()
        check_in_date, check_out_date = dt.strptime(criteria["check_in_date"],"%Y-%m-%d").date() , dt.strptime(criteria["check_out_date"],"%Y-%m-%d").date()
        units = DB.searchUnits(criteria)
        multipler = Unit.calculateMultipler(check_in_date, check_out_date, DB)
        for unit in units:
            unit["price"] = round(float(unit["price"]) * multipler)
            unit_id = unit['id']
            unit_price = unit['price']
            dataToken = f'{{"id": {unit_id}, "price": {unit_price}}}'
            unit["token"] = create_access_token(identity=dataToken,expires_delta=timedelta(hours=5))
        if units:
            code = 200
        else:
            code = 404
        return jsonify(units), code


@app.route("/informes")
@jwt_required()
def generateReports():
    message = {}
    recipient = json.loads(get_jwt_identity()).get("username")
    # recipient = "guillermo.fullstack@gmail.com"
    message, code = reports.sendReports(app, recipient, DB, render_template("/mails/informes.html"))
    # for recipient in ["guillermo.fullstack@gmail.com","carol.ceron801@gmail.com","germangp62@gmail.com","msoledadm88@gmail.com"]:
    #     message[recipient] = reports.sendReports(app, mail,recipient,DB)
    return jsonify(message), code


@app.route("/api/terceros/almacenaReserva", methods = ['POST'])
@jwt_required()
def saveReservation():
    try:
        data_token = json.loads(get_jwt_identity())
        unit_id = data_token.get("id")
        unit_price = data_token.get("price")
        data = request.get_json()
        dataGuest = data.get("guest")
        if unit_id == data.get("unit_id"):
            guest = Guest(dataGuest.get("name"), dataGuest.get("mail"),dataGuest.get("phone"),DB)
            guestId = guest.save()
            reservation = Reservation(unit_id, guestId, dt.strptime(data.get("check_in_date"),"%Y-%m-%d"), dt.strptime(data.get("check_out_date"),"%Y-%m-%d"), unit_price, data.get("amount_paid"), DB)
            return jsonify(reservation.save()), 201
        else:
            return jsonify({"message":"error en el token, reserva no almacenada"}), 403
    except json.JSONDecodeError:
        return jsonify({"message":"Error: La identidad del token no es un JSON válido."}), 400
        

@app.route("/motor", methods = ['POST','GET'])
@jwt_required()
def datos_multiplicador():
    if request.method == "POST":
        data = request.get_json()
        count = DB.setSeasonRates(data)
        return jsonify({"message": "Se han creado {count} periodos correctamente."}), 201
    lista = DB.getSeasonRates()
    if lista:
        code = 200
    else:
        code = 404 
    return jsonify(lista), code

@app.route("/verReservas")
def getReservations():
    lista = DB.getDataReservation()
    if lista:
        code = 200
    else:
        code = 404 
    return jsonify(lista), code

@app.route("/enviarLinkCheckin")
def sendLinkCheckin():
    tomorrow = dt.today().date()-timedelta(hours=3) + timedelta(days=1)
    print(tomorrow)
    reservationsForTomorrow = DB.getReservation_mail(tomorrow)
    print(reservationsForTomorrow)
    urlFront = os.getenv("URL_FRONT")
    messages = {}
    for reservation in reservationsForTomorrow:
        link = f"{urlFront}/checkin/{reservation[0]}"
        messages[reservation[1]] = sendMail(app,reservation[1],"Chek-in",[],render_template("/mails/checkin.html", link=link))[0]["message"]
    return jsonify(messages), 200

@app.route("/checkin")
def checkin():
    id = request.args.get('id')
    unitTitle = DB.getUnitForReservationById(id)
    if unitTitle:
        DB.setCheckedIn(id)
        return jsonify({"message":"Check-in realizado con éxito","unit":unitTitle[0]}), 200
    return jsonify({"message":"Reserva no encontrada"}),400

if __name__ == "__main__":
     app.run(debug=True, host="localhost", port=5001)