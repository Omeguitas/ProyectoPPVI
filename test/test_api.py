import pytest
import datetime
import requests

BASE_URL = "http://localhost:5000"

HEADERS_ADMIN = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODQ2OTgwMSwianRpIjoiMGJhODgzZmMtNDM5Ny00OTNiLTkyZmItZmM0NGRiMGUwNGI4IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IntcInN1cGVyVXNlclwiOiAxLCBcInVzZXJuYW1lXCI6IFwiZ3VpbGxlcm1vLmZ1bGxzdGFja0BnbWFpbC5jb21cIn0iLCJuYmYiOjE3NDg0Njk4MDEsImNzcmYiOiIxOGYwY2M2OC0wOTQwLTQwMDUtYjRmYy1kMGVhM2UxNjhiMjQiLCJleHAiOjE3NTcxMDk4MDF9.nnCKkY4O4_SYhFSIWoFfPA4oUjNjd5TDHsJM6DF73E0"
}

HEADERS_USER = {
    "Content-Type": "application/json",
    "Authorization": ""
}

ID = 0

# def test_login():
#     url = f"{BASE_URL}/login"
#     data = {
#         "username": "guillermo.fullstack@gmail.com",
#         "password": "1234"
#     }
#     response = requests.post(url, json=data)
#     assert response.status_code == 200
#     assert "access_token" in response.json()

# def test_register_admin():
#     url = f"{BASE_URL}/crearAdmin"
#     data = {
#         "username": "carol.ceron801@gmail.com",
#         "password": "1234",
#         "superUser": "True"
#     }
#     response = requests.post(url, json=data, headers=HEADERS_ADMIN)
#     assert response.status_code == 200 or response.status_code == 201

# def test_ver_admins():
#     url = f"{BASE_URL}/verAdmins"
#     response = requests.get(url, headers=HEADERS_ADMIN)
#     assert response.status_code == 200 or response.status_code == 403

# def test_crear_unidad():
#     url = f"{BASE_URL}/creaUnidad"
#     data = {
#         "rooms": 2,
#         "beds": 4,
#         "title": f"Cabaña estilo americana con vista al lago{datetime.date.today()}",
#         "price": 1000,
#         "amenities": "cocina,baño,balcon,ducha",
#         "urls_fotos": "[https://res.cloudinary.com/...jpg]",
#         "bathrooms": 2,
#         "address": "Una calle"
#     }
#     response = requests.post(url, json=data, headers=HEADERS_ADMIN)
#     assert response.status_code == 200 or response.status_code == 201

# def test_editar_unidad():
#     url = f"{BASE_URL}/editarUnidad"
#     data = {
#         "rooms": 2,
#         "beds": 4,
#         "title": "Cabaña estilo americana con vista al lago",
#         "price": 1000,
#         "amenities": "cocina,baño,balcon,ducha",
#         "urls_fotos": "[https://res.cloudinary.com/...jpg]",
#         "bathrooms": 2,
#         "address": "Una calle",
#         "id":6
#     }
#     response = requests.post(url, json=data, headers=HEADERS_ADMIN)
#     assert response.status_code == 200

def test_consultar_unidades():
    url = f"{BASE_URL}/api/terceros/units/"
    data = {"check_in_date": "2025-9-20",
    "check_out_date": "2025-9-25"}
    response = requests.post(url, json=data, headers=HEADERS_ADMIN)
    unidad1 = response.json()[0]
    ID = unidad1["id"]
    cadena = "Bearer: "+ unidad1["token"]
    HEADERS_USER["Authorization"] = "Bearer:", unidad1["token"]
    assert response.status_code == 200
    



def test_generar_reserva():
    url = f"{BASE_URL}/api/terceros/almacenaReserva"
    data = {
        "unit_id": ID,
        "check_in_date": "2025-6-20",
        "check_out_date": "2025-6-25",
        "amount_paid": 250,
        "guest": {
            "name": "Sole",
            "mail": "guillermo.fullstack@gmail.com",
            "phone": "12345678"
        }
    }
    print(HEADERS_USER)
    response = requests.post(url, json=data, headers=HEADERS_USER)
    assert response.status_code == 200 or response.status_code == 201