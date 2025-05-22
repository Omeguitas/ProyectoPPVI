

class Guest:
    def __init__(self, name: str, email: str, phone: str, DB, id: int = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.id = id
        self.DB = DB

    def save(self):
        id = self.DB.saveGuest(self)
        return id
