from clases.reports import generateoccupationData
class Unit:
    def __init__(self, rooms: int, beds: int, description: str, price: float, amenities: list, urls_fotos: list, DB, id = None):
        self.rooms = rooms
        self.beds = beds
        self.description = description
        self.price = price
        self.amenities = amenities
        self.urls_fotos = urls_fotos
        self.DB = DB
        self.id = id

    def save(self):
        if not(self.rooms and self.beds and self.price):
            return '{"msg":"datos incompletos"}'
        else:
            return self.DB.createUnit(self)
        
    def edit(self):
        if not(self.rooms and self.beds and self.price):
            return '{"msg":"datos incompletos"}'
        else:
            return self.DB.modifyUnit(self)
        
    @staticmethod
    def calculateMultipler(since, until, DB):
        percentages = generateoccupationData(DB, "d", since, until)[1]
        avgPercentages = sum(percentages)/len(percentages)
        # TODO manejar cuando no todos los dias tienen multiplicador
        multiplerSeason = DB.getSeasonRates(since,until)
        if multiplerSeason:
            avgMultiplerSeason = sum(element[0] for element in multiplerSeason)/len(multiplerSeason)
        else:
            avgMultiplerSeason = 1
        multipler = 1 + avgPercentages + avgMultiplerSeason
        multipler = (1 + avgPercentages/100) * avgMultiplerSeason
        return multipler


""""
pi*Ocupacion*temporada
PI * (o+t)

10 * 2 * 0.3 =60
10 *(2+3) =50
"""