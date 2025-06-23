import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import date as dt, timedelta as td
from dotenv import load_dotenv
from clases.sendMail import sendMail

load_dotenv() 

def sendReports(app, recipient,DB,html):
    '''Prepara los informes y los envia por mail al administrador que los solicito'''
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
    '''Busca los datos y genera el informe de ingresos'''
    incomeData = DB.getIncomeData()
    months = [data[0] for data in incomeData]
    income = [data[1] for data in incomeData]
    plt.figure(figsize=(8, 6))
    plt.bar(months, income)
    plt.xlabel('Mes')
    plt.ylabel('Monto')
    plt.title('Ingresos Mensuales')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    for month, amount in zip(months, income):
        plt.text(month, amount / 2, str(amount), ha='center', va='center', color='white', rotation=90) # agrego el monto

    # Guardar el gráfico en un buffer de memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer


def generateOcupationReport(DB):
    '''Busca los datos y genera el informe de ocupación'''
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
            plt.text(period, ocupation / 2, f'{ocupation}%', ha='center', va='center', color='white', rotation=90) # agrego el valor

        # Guardar el gráfico en un buffer de memoria
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        buffers.append((buffer,title))
        i += 1
    return buffers


def generateoccupationData(DB, groupBy:str= "month", inicio:dt = None, fin:dt = None):
    '''Busca los datos de ocupación'''
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