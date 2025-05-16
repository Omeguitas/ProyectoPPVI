

class Admin:
    def __init__(self, db, username:str, password:str, superUser:bool=False):
        self.username = username
        self.pasword = password
        self.superUser = superUser
        self.authenticated = False
        self.DB = db


    def save(self):
        return self.DB.createAdmin(self)
        
    
    def authenticate(self):
        result = self.DB.searchAdmin(self)
        if type(result) == tuple:
            self.superUser = result[0]
            self.authenticated = True
            

    def addUnity(self,unity):
        pass