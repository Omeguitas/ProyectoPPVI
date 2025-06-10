import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import json
import os
import smtplib
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from flask_mail import Mail, Message
from datetime import date as dt, timedelta as td
from dotenv import load_dotenv

load_dotenv() 

def sendMail(app, recipient, message:str,files:list, html:str=""):
    sender=app.config['MAIL_DEFAULT_SENDER']
    msg = Message(message,
        sender=sender,
        recipients=[recipient]
    )
    msg.body = message
    msg.html = (html)
    for file in files:
        msg.attach(file[0],file[1],file[2])

    creds = obtener_credenciales()
    try:
    # Conexión con el servidor de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        auth_string = base64.b64encode(
            f"user={sender}\1auth=Bearer {creds.token}\1\1".encode("utf-8")
        ).decode("utf-8")
        server.docmd("AUTH", "XOAUTH2 " + auth_string)
        server.sendmail(sender, recipient, msg.as_string().encode('utf-8'))
        server.quit()
        return {"message":"Correo electrónico enviado con éxito."}
    except Exception as e:
        return {"message":"Error al enviar el correo electrónico: {e}"}


def sendReports(app, recipient,DB,html):
    files = []
    bufferIncomeReports = generateIncomeReports(DB)
    bufferoccupationReport = generateOcupationReport(DB)
    if bufferoccupationReport:
        for buffer in bufferoccupationReport:
            buffer[0].seek(0)
            files.append((f"{buffer[1]}.png", "image/png", buffer[0].read()))
    if bufferIncomeReports:
        bufferIncomeReports.seek(0)
        files.append(("ingresos_mensuales.png", "image/png", bufferIncomeReports.read()))
    message = "Adjunto encontrarás los informes de ingresos y ocupación en formato de imagen."
    respuesta = sendMail(app, recipient, message,files,html=html)
    return respuesta
    

def generateIncomeReports(DB):
    incomeData = DB.getIncomeData()
    # months = [data[0] for data in incomeData]
    # income = [data[1] for data in incomeData]
    months = ["1-24","2-24","3-24","4-24","5-24","6-24","7-24","8-24","9-24","10-24","11-24","12-24"]
    income = [40000,150000,100000,35000,50000,225000,200000,100000,300000,400000,50000,20000]
    

    plt.figure(figsize=(8, 6))
    plt.bar(months, income)
    plt.xlabel('Mes')
    plt.ylabel('Monto')
    plt.title('Ingresos Mensuales')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    for month, amount in zip(months, income):
        plt.text(month, amount / 2, str(amount), ha='center', va='center', color='white', rotation=90) #agrego el monto

    # Guardar el gráfico en un buffer de memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer


def generateOcupationReport(DB):
    
    
    periods, ocupations = generateoccupationData(DB, "m")
    i = 0
    buffers = []
    while i < len(periods)/30:
        subGroupPeriods, subGroupOcupations = periods[i*30:(i+1)*30], ocupations[i*30:(i+1)*30]
        title = f"Ocupación {subGroupPeriods[0]}/{subGroupPeriods[-1]}"
        plt.figure(figsize=(8, 6))
        plt.bar(subGroupPeriods, subGroupOcupations)
        plt.xlabel('Mes')
        plt.ylabel('Ocupación')
        plt.title(title)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.ylim(0,100)

        for period, ocupation in zip(subGroupPeriods, subGroupOcupations):
            plt.text(period, ocupation / 2, f'{ocupation}%', ha='center', va='center', color='white', rotation=90) #agrego el monto

        # Guardar el gráfico en un buffer de memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        buffers.append((buffer,title))
        i += 1
    return buffers


def generateoccupationData(DB, groupBy:str= "month", inicio:dt = None, fin:dt = None):
    reservations = DB.getReservations()
    numberOfUnits = DB.getTotalUnits()
    strGroupBy = ""
    match groupBy.lower():
        case "y" | "year" :
            strGroupBy = "%Y"
        case "m" | "month":
            strGroupBy = "%Y-%m"
        case "d" | "day":
            strGroupBy = "%Y-%m-%d"
        case _:
            return "cadena incorrecta para groupBy"
    if not inicio:
        inicio = reservations[0][3]
    if not fin:
        fin = max([i[4] for i in reservations])

    fin = (fin+td(days=32-fin.day)).replace(day = 1)-td(days=1)
    actual = inicio.replace(day=1)
    days = []
    ocupations = []
    while actual <= fin:
        days.append(actual)
        suma = 0
        for reservation in reservations:
            if actual >= reservation[3] and actual <= reservation[4]:
                suma += 1
        ocupations.append(suma * 100 / numberOfUnits[0] )
        actual+=td(days=1)
    dictionary = {}
    for day, ocupation in zip(days, ocupations):
        if not dictionary.get(day.strftime(strGroupBy), False):
            dictionary[day.strftime(strGroupBy)] = []
        dictionary[day.strftime(strGroupBy)].append(ocupation)
    period = []
    percentages = []
    for key,value in dictionary.items():
        period.append(key)
        percentages.append(round(sum(value)/len(value), 2))
    return period, percentages



SCOPES = [
    'https://mail.google.com/',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

def obtener_credenciales():
    """Obtiene las credenciales de OAuth 2.0 desde variables de entorno.
    """
    creds = None

    token_json_str = os.environ.get("GOOGLE_TOKEN_JSON")
    if token_json_str:
        try:
            # Parsear la cadena JSON de la variable de entorno
            creds_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
        except Exception as e:
            print(f"Error al cargar credenciales desde GOOGLE_TOKEN_JSON: {e}")
            creds = None # Si hay un error, se descartará y pasará al siguiente paso.

    if not creds and os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    if not creds or not creds.valid:
        client_id = os.environ.get("CLIENT_ID")
        client_secret = os.environ.get("CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "CLIENT_ID y CLIENT_SECRET deben estar configuradas en las variables de entorno."
            )

        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "redirect_uris": ["http://localhost:8080"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "client_secret": client_secret
                }
            },
            SCOPES,
        )
        creds = flow.run_local_server(port=8080)
    # Guarda las credenciales para la próxima ejecución.
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


