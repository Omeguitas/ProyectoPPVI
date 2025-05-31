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
                r.check_out_date > %s AND r.check_in_date < %s )"""
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
            # Crear un diccionario para cada fila, usando zip para emparejar nombres y valores
            unit_dicc = dict(zip(columns_name, unit))
            dicc_list.append(unit_dicc)
        return dicc_list

    def createUnit(self, unit):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """INSERT INTO unit (rooms, beds, description, price, amenities, urls_fotos) VALUES(%s,%s,%s,%s,%s,%s)"""
        data = unit.rooms, unit.beds, unit.description, unit.price, json.dumps(unit.amenities),unit.urls_fotos
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
        urls_fotos = %s
        WHERE id LIKE %s"""
        data = (unit.rooms, unit.beds, unit.description, unit.price, json.dumps(unit.amenities), unit.urls_fotos, unit.id)
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
            message = "{'message':'Unidad eliminada con exito'}"
        else:
            message = "{'message':'Unidad no encontrada'}"
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

    

    def generateReservation(self):
        pass


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
            GROUP BY mes
            ORDER BY mes;
            """)
        data = cursor.fetchall()
        conn.close()
        return data
    
    def getReservations(self, since = datetime.min, until=datetime.max):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservation  WHERE check_in_date BETWEEN %s AND %s ORDER BY check_in_date",(since,until))
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
        


    def getSeasonRates(self, since, until):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT multiplier FROM season_rates WHERE"""
        actual = since
        fechas = []
        while actual < until:
            query += "%s BETWEEN since AND until OR"
            fechas.append(actual)
            actual += td(days=1)
        query += "%s BETWEEN since AND until"
        fechas.append(actual)
        cursor.execute(query,fechas)
        result = cursor.fetchall()
        conn.close()
        return result
