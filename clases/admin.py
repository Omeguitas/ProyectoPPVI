

class Admin:
    def __init__(self, db, username:str, password:str, superUser:bool=False):
        self.username = username
        self.password = password
        self.superUser = superUser
        self.authenticated = False
        self.DB = db


    def save(self):
        return self.DB.createAdmin(self)
        
    
    def authenticate(self):
        self.DB.autenticateAdmin(self)
        
            
