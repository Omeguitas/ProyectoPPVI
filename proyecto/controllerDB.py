from flaskext.mysql import MySQL
from datetime import datetime



database = "my_database"
mysql = MySQL()

def initDB():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
    conn.commit()
    # Creación de la tabla `admin` (administrador)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`admin`(
                   `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
                   `username` VARCHAR(30) UNIQUE,
                   `password` VARCHAR(30),
                   `superUser` BOOLEAN
                   )""")
    # Creación de la tabla `guest` (huésped)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`guest`(
        `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
        `name` VARCHAR(255) NOT NULL,
        `email` VARCHAR(255) UNIQUE NOT NULL,
        `phone` VARCHAR(20)
    )""")

    # Creación de la tabla `unit` (unidad)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`unit`(
        `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
        `rooms` INT(10) NOT NULL,
        `beds` INT(10) NOT NULL,
        `description` TEXT,
        `price` DECIMAL(10, 2) NOT NULL
    )""")

    # Creación de la tabla `reservation` (reserva)
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`reservation`(
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
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`survey`(
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
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`survey_question`(
        `id` INT(10) PRIMARY KEY AUTO_INCREMENT,
        `question_text` VARCHAR(255) NOT NULL,
        `question_type` VARCHAR(50) NOT NULL,  -- Tipo de respuesta: 'escala', 'texto', 'opcion multiple', etc.
        `options` TEXT,                       -- Opciones para preguntas de opción múltiple o escala (JSON)
        `order` INT(10) NOT NULL             --Para definir el orden de las preguntas
    )""")

    # -- Tabla para almacenar las respuestas de los huéspedes a las preguntas de la encuesta
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS `{database}`.`survey_response`(
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


def searchUnits(criteria: dict):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = """SELECT * FROM unit u WHERE u.id NOT IN
      (SELECT r.unit_id FROM reservation r WHERE
        r.check_out_date > %s AND r.check_in_date < %s )"""

    params = [criteria.pop("start_date"), criteria.pop("end_date")]

    for key, value in criteria:
        query += f" AND {key} = " + "%s"
        params.add(value)

    cursor.execute(query, params)
    units = cursor.fetchall()
    conn.close()
    return units

def createUnit():
    pass

def modifyUnit():
    pass

def deleteUnit():
    pass

def searchAdmin(username: str, password: str):
    conn = mysql.connect()
    cursor = conn.cursor()
    # hashear password?
    query = """SELECT superUser FROM admin WHERE username LIKE %s AND password LIKE %s"""
    cursor.execute(query,(username,password))
    result = cursor.fetchone()
    conn.close()
    return result

def createAdmin():
    pass

def generateReservation():
    pass

