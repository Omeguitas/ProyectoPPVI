import matplotlib.pyplot as plt
import io
from flask_mail import Mail, Message
# from controllerDB import ControllerDB as DB
from datetime import date as dt, timedelta as td


def sendReports(app, mail, recipient):
    bufferIncomeReports = generateIncomeReports()
    bufferoccupationReport = generateoccupationReport()
    
    msg = Message(
        "Informes de ingresos y ocupación",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = "Adjunto encontrarás los informes de ingresos y ocupación."
    msg.html = (
        "Adjunto encontrarás los informes de ingresos y ocupación en formato de imagen."
    )  # mensaje en html

    # Adjuntar el gráfico al correo electrónico
    bufferIncomeReports.seek(0)
    bufferoccupationReport.seek(0)
    msg.attach("ingresos_mensuales.png", "image/png", bufferIncomeReports.read())
    msg.attach("ocupación_mensual.png", "image/png", bufferoccupationReport.read())
    try:
        mail.send(msg)
        return '{"message":"Correo electrónico enviado con éxito."}'
    except Exception as e:
        return '{"message":"Error al enviar el correo electrónico: {e}"}'

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


def generateoccupationReport(DB, *arg, **kwargs):
    reservations = DB.getReservations(*arg, **kwargs)
    numberOfUnits = DB.getTotalUnits()
    months, occupations = generateoccupationData(reservations, numberOfUnits, *arg, **kwargs)
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