from flaskext.mysql import MySQL
from datetime import datetime
from werkzeug.security import generate_password_hash as hashear, check_password_hash

# import clases.admin



class controllerDB:
    def __init__(self, mysql: MySQL):
        self.mysql = mysql

    def createDB(self, nameDB: str):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nameDB}")
        conn.commit()
        conn.close()

    def initDB(self):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        # Creación de la tabla `admin` (administrador)
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `admin`(
                    `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
                    `username` VARCHAR(30) UNIQUE,
                    `password` VARCHAR(255),
                    `superUser` BOOLEAN
                    )""")
        # Creación de la tabla `guest` (huésped)
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `guest`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `name` VARCHAR(255) NOT NULL,
            `email` VARCHAR(255) UNIQUE NOT NULL,
            `phone` VARCHAR(20)
        )""")

        # Creación de la tabla `unit` (unidad)
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `unit`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `rooms` INT(10) NOT NULL,
            `beds` INT(10) NOT NULL,
            `description` TEXT,
            `price` DECIMAL(10, 2) NOT NULL
        )""")

        # Creación de la tabla `reservation` (reserva)
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `reservation`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `unit_id` INT(10) NOT NULL,
            `guest_id` INT(10) NOT NULL,
            `check_in_date` DATE NOT NULL,
            `check_out_date` DATE NOT NULL,
            `price` DECIMAL(10, 2) NOT NULL,
            `amount_paid` DECIMAL(10, 2) NOT NULL,
            `checked_in` BOOLEAN NOT NULL DEFAULT FALSE,
            FOREIGN KEY (`unit_id`) REFERENCES `unit`(`id`),
            FOREIGN KEY (`guest_id`) REFERENCES `guest`(`id`)
        )""")

        # Creación de la tabla `survey` (encuesta)
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `survey`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `reservation_id` INT(10) NOT NULL,
            `question1` VARCHAR(255),
            `question2` VARCHAR(255),
            `question3` VARCHAR(255),
            `question4` VARCHAR(255),
            `question5` VARCHAR(255),
            `question6` VARCHAR(255),
            FOREIGN KEY (`reservation_id`) REFERENCES `reservation`(`id`)
        )""")


        '''
            OPCION DE ALMACENAR PREGUNTAS EN DB PARA DAR POSIBILIDAD AL ADMIN DE CREAR/ELIMINAR PREGUNTAS
            # Creación de la tabla `survey_question` (preguntas encuesta)

            # -- Tabla para almacenar las preguntas de la encuesta
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `survey_question`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `question_text` VARCHAR(255) NOT NULL,
            `question_type` VARCHAR(50) NOT NULL,  -- Tipo de respuesta: 'escala', 'texto', 'opcion multiple', etc.
            `options` TEXT,                       -- Opciones para preguntas de opción múltiple o escala (JSON)
            `order` INT(10) NOT NULL             --Para definir el orden de las preguntas
        )""")

        # -- Tabla para almacenar las respuestas de los huéspedes a las preguntas de la encuesta
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS `survey_response`(
            `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
            `reservation_id` INT(10) NOT NULL,
            `question_id` INT(10) NOT NULL,
            `response_text` TEXT,
            `response_scale` INT(10),             -- Para respuestas de tipo escala
            `response_option` VARCHAR(255),       -- Para respuestas de opción múltiple
            FOREIGN KEY (`reservation_id`) REFERENCES `reservation`(`id`),
            FOREIGN KEY (`question_id`) REFERENCES `survey_question`(`id`)
        )""")

        '''
        conn.commit()
        conn.close()


    def searchUnits(self, criteria: dict):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        query = """SELECT * FROM unit u WHERE u.id NOT IN
        (SELECT r.unit_id FROM reservation r WHERE
            r.check_out_date > %s AND r.check_in_date < %s )"""

        params = [criteria.pop("start_date"), criteria.pop("end_date")]

        for key, value in criteria.items():
            query += f" AND u.{key} = " + "%s"
            params.append(value)

        cursor.execute(query, params)
        units = cursor.fetchall()
        conn.close()
        return units

    def createUnit(self):
        pass

    def modifyUnit(self):
        pass

    def deleteUnit(self):
        pass

    def searchAdmin(self, admin):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        # hashear password?
        query = """SELECT superUser, password FROM admin WHERE username LIKE %s"""
        cursor.execute(query,(admin.username))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def autenticateAdmin(self, admin):
        result = self.searchAdmin(admin)
        if result and check_password_hash(result[1],admin.password):
            admin.superUser = result[0]
            return True
        return False

    def createAdmin(self, admin):
        try:
            conn = self.mysql.connect()
            cursor = conn.cursor()
            query = """INSERT INTO admin (username, password, superUser) VALUES(%s,%s,%s)"""
            # print(admin.username,admin.pasword,admin.superUser,"************")
            cursor.execute(query,(admin.username,hashear(admin.pasword),admin.superUser))
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
        for admin in admins:
            print(admin)
        return admins