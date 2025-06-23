from flask_mail import Mail, Message
import smtplib
import base64
import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://mail.google.com/',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def sendMail(app, recipient, message:str,files:list, html:str=""):
    '''Envio de mails'''
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
        return {"message":"Correo electrónico enviado con éxito."},200
    except Exception as e:
        return {"message":"Error al enviar el correo electrónico: {e}"},408
    


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
    # Guarda las credenciales en token.json
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds