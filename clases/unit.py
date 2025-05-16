class Unit:
    def __init__(self, rooms: int, beds: int, description: str, price: float, amenities: list, urls_fotos: list, DB):
        self.rooms = rooms
        self.beds = beds
        self.description = description
        self.price = price
        self.amenities = amenities
        self.urls_fotos = urls_fotos
        self.DB = DB

    def save(self):
        if not(self.rooms and self.beds and self.price):
            return '{"msg":"datos incompletos"}'
        else:
            return self.DB.createUnit(self)