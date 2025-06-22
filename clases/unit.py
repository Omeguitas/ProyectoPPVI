from clases.reports import generateoccupationData
import datetime as dt
class Unit:
    def __init__(self, rooms: int, beds: int, description: str, price: float, amenities: list, urls_fotos: list, DB,title,bathrooms,address, id = None):
        self.rooms = rooms
        self.beds = beds
        self.description = description
        self.price = price
        self.amenities = amenities
        self.urls_fotos = urls_fotos
        self.DB = DB
        self.id = id
        self.title = title
        self.bathrooms = bathrooms
        self.address = address

    def save(self):
        '''Guarda unidad en DB'''
        if not(self.rooms and self.beds and self.price and self.title and self.bathrooms and self.address):
            return {"msg":"datos incompletos"}, 400
        else:
            return self.DB.createUnit(self)
        
    def edit(self):
        if not(self.rooms and self.beds and self.price and self.title and self.bathrooms and self.address):
            return {"msg":"datos incompletos"}, 400
        else:
            return self.DB.modifyUnit(self)
        
    @staticmethod
    def calculateMultipler(since:dt.date, until:dt.date, DB):
        duration = until.day-since.day
        percentages = generateoccupationData(DB, "d", since, until)[1]
        avgPercentages = sum(percentages)/len(percentages)
        multiplierSeason = [element['multiplier'] for element in DB.getSeasonRates(since,until)]
        difference = duration-len(multiplierSeason)
        while difference > 0:
            multiplierSeason.append(1)
            difference -= 1
        avgMultiplierSeason = sum(multiplierSeason)/len(multiplierSeason)
        multipler = (1 + avgPercentages/100) * avgMultiplierSeason
        return multipler
