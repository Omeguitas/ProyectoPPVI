from flaskext.mysql import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash as hashear, check_password_hash
import json
from datetime import timedelta as td

# import clases.admin




class ControllerDB:
    def __init__(self, mysql: MySQL):
        self.mysql = mysql

    def searchUnits(self, criteria: dict = None):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT * FROM unit u"""
        params = []
        if criteria:
            query += " WHERE"
            check_in_date = criteria.pop("check_in_date", False)
            check_out_date = criteria.pop("check_out_date", False)
            if (check_in_date and check_out_date):
                query += """ u.id NOT IN
                (SELECT r.unit_id FROM reservation r WHERE
                r.check_out_date > %s AND r.check_in_date < %s AND NOT r.canceled )"""
                params = [check_in_date, check_out_date]
            
            amenities = criteria.pop("amenities",False)
            if amenities:
                if not(check_in_date and check_out_date):
                    query += " 1=1" # Condición que no modifica el resultado, pero simplifica el armado de la query
                for amenitie in amenities:
                    query += """ AND FIND_IN_SET(%s, amenities)"""
                    params.append(amenitie)

            if not(amenities or check_in_date and check_out_date):
                query += " 1=1" # Condición que no modifica el resultado, pero simplifica el armado de la query
            for key, value in criteria.items():
                query += f" AND u.{key} = " + "%s"
                params.append(value)
        cursor.execute(query, params)
        units = cursor.fetchall()
        conn.close()
        columns_name = [description[0] for description in cursor.description]

        # Construir la lista de diccionarios
        dicc_list = []
        for unit in units:
            unit_dicc = dict(zip(columns_name, unit))
            dicc_list.append(unit_dicc)
        return dicc_list

    def createUnit(self, unit):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """INSERT INTO unit (rooms, beds, description, price, amenities, urls_fotos,title,bathrooms,address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        data = unit.rooms, unit.beds, unit.description, unit.price, json.dumps(unit.amenities),unit.urls_fotos,unit.title,unit.bathrooms,unit.address
        cursor.execute(query,data)
        conn.commit()
        conn.close()
        return '{"msg":"Unidad creada con exito"}'
    

    def modifyUnit(self, unit):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """UPDATE unit SET
            rooms = %s,
            beds = %s,
            description = %s,
            price = %s,
            amenities = %s,
            urls_fotos = %s,
            title = %s,
            bathrooms = %s,
            address = %s
            WHERE id LIKE %s"""
        data = (unit.rooms, unit.beds, unit.description, unit.price, json.dumps(unit.amenities), unit.urls_fotos,unit.title,unit.bathrooms,unit.address, unit.id)
        cursor.execute(query,data)
        conn.commit()
        message = ""
        if cursor.rowcount:
            message = "{'message':'Unidad modificada con exito'}"
        else:
            message = "{'message':'Unidad no encontrada'}"
        cursor.close()
        conn.close()
        return message
        
    
    def deleteUnit(self, id):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """DELETE FROM unit WHERE id LIKE %s"""
        cursor.execute(query,id)
        conn.commit()
        message = ""
        if cursor.rowcount:
            message = {'message':'Unidad eliminada con exito'}, 200
        else:
            message = {'message':'Unidad no encontrada'}, 404
        cursor.close()
        conn.close()
        return message

    def searchAdmin(self, admin):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT superUser, password FROM admin WHERE username LIKE %s"""
        cursor.execute(query,(admin.username))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def autenticateAdmin(self, admin):
        result = self.searchAdmin(admin)
        if result and check_password_hash(result[1],admin.password):
            admin.authenticated = True
            admin.superUser = result[0]
            return True
        return False

    def createAdmin(self, admin):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = """INSERT INTO admin (username, password, superUser) VALUES(%s,%s,%s)"""
            data = (admin.username,hashear(admin.password),admin.superUser=="True")
            cursor.execute(query,data)
            conn.commit()
            conn.close()
            return f"{admin.username} registrado exitosamente"
        except:
            return "Administrador ya registrado"

    def deleteAdmin(self, id:int):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = "DELETE FROM admin WHERE id = %s"
        deleted = cursor.execute(query,(id)) > 0
        conn.commit()
        conn.close()
        return deleted
    
    def modifyPassAdmin(self,username,password):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = "UPDATE admin SET password = %s WHERE username = %s"
        modified = cursor.execute(query,(hashear(password),username)) > 0
        conn.commit()
        conn.close()
        return modified


    def auxVerAdmins(self):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin")
        admins = cursor.fetchall()
        return admins
    
    def getIncomeData(self):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("""SELECT 
            DATE_FORMAT(check_in_date, '%Y-%m') AS mes,
            SUM(price) AS ingresos
            FROM reservation
            WHERE NOT canceled
            GROUP BY mes
            ORDER BY mes;
            """)
        data = cursor.fetchall()
        conn.close()
        return data
    
    def getReservations(self, since = datetime.min, until=datetime.max):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservation  WHERE NOT canceled AND check_in_date BETWEEN %s AND %s ORDER BY check_in_date",(since,until))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def getTotalUnits(self):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id) FROM unit")
        numberOfUnits = cursor.fetchone()
        conn.close()
        return numberOfUnits

    def searchIdGuestByMail(self, guest):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM guest WHERE email = %s", guest.email)
        idGuest = cursor.fetchone()
        conn.close()
        return idGuest
    
    def saveGuest(self, guest):
        id = None
        result = self.searchIdGuestByMail(guest)
        if result:
            id = result[0]
        else:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = """INSERT INTO guest (name, email, phone) VALUES(%s,%s,%s)"""
            data = (guest.name, guest.email, guest.phone)
            cursor.execute(query, data)
            conn.commit()
            id = cursor.lastrowid
            conn.close()
        return id
    
    def createReservation(self, reservation):
        if self.searchUnits({"check_in_date":reservation.check_in_date,"check_out_date": reservation.check_out_date,"id":reservation.unit_id}):
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = """INSERT INTO reservation (unit_id, guest_id, check_in_date, check_out_date, price, amount_paid) VALUES(%s,%s,%s,%s,%s,%s)"""
            data = (reservation.unit_id, reservation.guest_id, reservation.check_in_date, reservation.check_out_date, reservation.price, reservation.amount_paid)
            cursor.execute(query,data)
            conn.commit()
            conn.close()
            return {"message":"Reserva exitosa"}
        return {"message":"La unidad ya se encuentra reservada en esas fechas"}
    

    def cancelReservation(self,id:int):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = "UPDATE reservation SET canceled = 1 WHERE id = %s"
        modificated = cursor.execute(query,(id))
        conn.commit()
        if modificated:
            return {"message":"Reserva cancelada"},201
        return {"message":"Reserva no encontrada"},400

        


    def getSeasonRates(self, since=None, until=None):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT * FROM season_rates"""
        fechas = []
        if since and until:
            query +=" WHERE"
            actual = since
            while actual < until:
                query += "%s BETWEEN since AND until OR"
                fechas.append(actual)
                actual += td(days=1)
            query += "%s BETWEEN since AND until"
            fechas.append(actual)
        cursor.execute(query,fechas)
        result = cursor.fetchall()
        conn.close()
        columns_name = [description[0] for description in cursor.description]
        dicc_list = []
        for season_rate in result:
            season_rates_dicc = dict(zip(columns_name, season_rate))
            season_rates_dicc['since'] = season_rates_dicc['since'].strftime("%Y-%m-%d")
            season_rates_dicc['until'] = season_rates_dicc['until'].strftime("%Y-%m-%d")
            dicc_list.append(season_rates_dicc)

        return dicc_list


    def setSeasonRates(self, data):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        queryDelete = """DELETE FROM season_rates"""
        cursor.execute(queryDelete)
        conn.commit()
        count = 0
        for element in data:
            queryInsert = """INSERT INTO season_rates (since, until, multiplier) VALUES(%s,%s,%s)"""
            values = (datetime.strptime(element[0],"%Y-%m-%d"),datetime.strptime(element[1],"%Y-%m-%d"),float(element[2]))
            count += cursor.execute(queryInsert,values)
        conn.commit()
        conn.close()
        return count


    def getDataReservation(self):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT r.check_in_date as Ingreso,
        r.check_out_date as Salida,
        r.price as Total,
        r.amount_paid as Pagado,
        r.checked_in,
        r.unit_id,
        u.urls_fotos as Foto,
        u.title as Unidad,
        g.name,
        g.email,
        r.id,
        r.canceled
        FROM reservation r
        JOIN unit u ON r.unit_id = u.id
        JOIN guest g ON r.guest_id = g.id
        ORDER BY Ingreso"""
        today = datetime.today().date()
        cursor.execute(query)
        reservations = cursor.fetchall()
        conn.close()
        columns_name = [description[0] for description in cursor.description]
        dicc_list_current = []
        dicc_list_future = []
        dicc_list_cancelled = []
        dicc_list_past = []
        for reservation in reservations:
            dicc = dict(zip(columns_name,reservation))
            dicc["Foto"] = dicc["Foto"].split(",")[0]
            # print(dicc)
            if dicc["canceled"]:
                dicc_list_cancelled.append(dicc)
            elif dicc["Salida"] >= today:
                print(dicc["Ingreso"],"****")
                if dicc["Ingreso"] <= today:
                    dicc_list_current.append(dicc)
                else:
                    dicc_list_future.append(dicc)
            else:
                dicc_list_past.append(dicc)
            dicc["Ingreso"] = datetime.strftime(dicc["Ingreso"],"%Y-%m-%d")
            dicc["Salida"] = datetime.strftime(dicc["Salida"],"%Y-%m-%d")

        return {"current":dicc_list_current, "future": dicc_list_future, "past": dicc_list_past, "cancelled": dicc_list_cancelled}

    def getReservation_mail(self, tomorrow:datetime, yesterday:datetime):
        data = []
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT r.id, g.email, g.name
            FROM reservation r
            JOIN guest g
            ON r.guest_id = g.id
            WHERE r.check_in_date BETWEEN %s AND %s"""
        cursor.execute(query,(tomorrow,tomorrow))
        data.append(cursor.fetchall())
        query = """SELECT r.id, g.email, g.name
            FROM reservation r
            JOIN guest g
            ON r.guest_id = g.id
            WHERE r.check_out_date BETWEEN %s AND %s"""
        cursor.execute(query,(yesterday,yesterday))
        data.append(cursor.fetchall())
        conn.close()
        return data
    
    def getUnitForReservationById(self, id:int):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT u.title
            FROM unit u
            JOIN reservation r
            ON r.unit_id = u.id
            WHERE r.id = %s
            AND NOT r.canceled"""
        cursor.execute(query,(id))
        unit_title = cursor.fetchone()
        conn.close()
        return unit_title
    
    def setCheckedIn(self, id:int):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """UPDATE reservation SET checked_in = 1 WHERE id = %s"""
        cursor.execute(query,(id))
        conn.commit()
        conn.close()

    def uploadSurvey(self, request):
        dicc = request.get_json()
        print(dicc, "^^^^^^^^^^^^^^^^ÑÑÑÑÑÑÑÑÑ")
        id = dicc.get("id")
        p1 = dicc.get("p1")
        p2 = dicc.get("p2")
        p3 = dicc.get("p3")
        p4 = dicc.get("p4")
        p5 = dicc.get("p5")
        data = (id,p1,p2,p3,p4,p5)
        query = "INSERT INTO survey (reservation_id, question1, question2, question3, question4 ,question5) VALUES(%s,%s,%s,%s,%s,%s)"
        conn = self.mysql.connect()
        cursor = conn.cursor()
        try:
            insert = cursor.execute(query,data)
            conn.commit()
            conn.close()
            return {"message":"Encuesta cargada"},201
        except Exception as e:
            return {"message":f"Encuesta cargada previamente {e}"},403
        

    def updateSuperAdmin(self, request):
        admins = request.get_json()
        query = "UPDATE admin SET superUser = %s WHERE id = %s"
        conn = self.mysql.connect()
        cursor = conn.cursor()
        a = {"2":"2"}
        for admin in admins:
            data = list(admin.values())[0], list(admin.keys())[0]
            cursor.execute(query,data)
        conn.commit()
        conn.close()
        return {"message":"Valores modificados con éxito"}