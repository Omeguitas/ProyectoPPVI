from datetime import date

class Reservation:
    def __init__(self, unit_id: int, guest_id: int, check_in_date: date, check_out_date: date, price: float, amount_paid: float, DB, id:int = None):
        self.unit_id = unit_id
        self.guest_id = guest_id
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.price = price
        self.amount_paid = amount_paid
        self.id = id
        self.DB = DB

    def save(self):
        
        pass