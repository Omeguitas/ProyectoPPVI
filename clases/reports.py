import matplotlib.pyplot as plt
import io
import os
import smtplib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from flask_mail import Mail, Message
from datetime import date as dt, timedelta as td
from dotenv import load_dotenv

load_dotenv() 

def sendMail(app, mail, recipient, message:str,files:list):
    msg = Message(message,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = message
    msg.html = ("")
    print(files,"******************")
    for file in files:
        msg.attach(file)

    creds = obtener_credenciales()
    sender = creds.from_addr

    try:
    # Conexión con el servidor de Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(sender, creds.token) # Usa el token obtenido
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        return '{"message":"Correo electrónico enviado con éxito."}'
    except Exception as e:
        return '{"message":"Error al enviar el correo electrónico: {e}"}' 


def sendReports(app, mail, recipient,DB):
    files = []
    bufferIncomeReports = generateIncomeReports(DB)
    bufferoccupationReport = generateoccupationReport(DB)
    if bufferoccupationReport:
        bufferoccupationReport.seek(0)
        files.append(bufferoccupationReport)
    if bufferIncomeReports:
        bufferIncomeReports.seek(0)
        files.append(bufferIncomeReports)
    message = "Adjunto encontrarás los informes de ingresos y ocupación en formato de imagen."
    sendMail(app, mail, recipient, message,files)
    

def generateIncomeReports(DB):
    incomeData = DB.getIncomeData()
    months = [data[0] for data in incomeData]
    income = [data[1] for data in incomeData]
    # monts = ["1-24","2-24","3-24","4-24","5-24","6-24","7-24","8-24","9-24","10-24","11-24","12-24"]
    # income = [40000,150000,100000,35000,50000,225000,200000,100000,300000,400000,50000,20000]
    

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


def generateoccupationReport(DB):
    reservations = DB.getReservations()
    numberOfUnits = DB.getTotalUnits()
    if reservations:
        months, occupations = generateoccupationData(reservations, numberOfUnits)
        plt.figure(figsize=(8, 6))
        plt.bar(months, occupations)
        plt.xlabel('Mes')
        plt.ylabel('Ocupación')
        plt.title('Ocupación Mensual')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        for month, occupation in zip(months, occupations):
            plt.text(month, occupation / 2, f'{occupation}%', ha='center', va='center', color='white', rotation=90) #agrego el monto

        # Guardar el gráfico en un buffer de memoria
        buffer = io.BytesIO()
        buffer.seek(0)
        plt.close()
        return buffer
    return None


def generateoccupationData(reservations,numberOfUnits, inicio = None, fin = None):
    if not inicio:
        inicio = dt(reservations[0][3])
    else:
        inicio = dt(inicio)
    if not fin:
        fin = max([dt(i[4]) for i in reservations])
    else:
        fin = dt(fin)

    actual = inicio
    days = [inicio]
    ocupations = []
    while actual <= fin:
        days.append(actual)
        sum = 0
        for reservation in reservations:
            if actual >= dt(reservation[3]) and actual <= dt(reservation[4]):
                sum += 1
        ocupations.append(sum * 100 / numberOfUnits )
        actual+=td(days=1)
    dictionary = {}
    for day, ocupation in zip(days, ocupations):
        if not dictionary.get(day.strftime("%Y-%m"), False):
            dictionary[day.strftime("%Y-%m")] = []
        dictionary[day.strftime("%Y-%m")].append(ocupation)
        months = []
        percentages = []
    for key,value in dictionary.items:
        months.append(key)
        percentages = sum(value)/len(value)
    return months, percentages



SCOPES = ['https://mail.google.com/']

def obtener_credenciales():
    """Obtiene las credenciales de OAuth 2.0 desde variables de entorno.
    """
    creds = None

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
                "redirect_uris": ["http://localhost:8080"],  # Añade esto
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        SCOPES,
    )
    creds = flow.run_local_server(port=0)
    # Guarda las credenciales para la próxima ejecución.
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


