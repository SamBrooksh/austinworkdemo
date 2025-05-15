import sqlite3
from enum import IntEnum
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

SQLDATABASE = "demo.db"
#Grab the stages from database and throw in dict of {id:name}
# Hmm, I may change how this works later - it would be nice if I could add it dynamically with the database
# But that typically will make it hard to use later - Maybe just a way to check that it's right
class stages(IntEnum):
    RECEIVED_REQUEST = 1
    pass
#This needs to match the values in client database

class client:
    email: str 

    def __init__(self, clientemail=""):
        self.email = clientemail

    def insert_rows():
        #Probably can make this more efficient at somepoint and then use this for insert - doing it lazy for now
        return f"email"
    
    def to_sql_client(self):
        return f"email = '{self.email}'"
    
    def insert(self):
        return f"'{self.email}'"

class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id 
        self.username = username
        #Password will be hashed
        self.password = password
        self.role = role
    
    def check_password(self, password):
        return self.password == password
        #return check_password_hash(self.password, password)

    def get_id(self)->str:
        return str(self.id)


# Attempts to find client in table, if not found makes one and adds new row to clientrequests
# With no receipt and Stage at RECEIVED_REQUEST
# Return the id of the row entered, or -1 for an error
def add_job(details:dict, cl: client)->int:
    #Should add a try except here
    with sqlite3.connect(SQLDATABASE) as conn:
        cursor = conn.cursor()
        get_client_command = f"SELECT * FROM client WHERE {cl.to_sql_client()}"
        print(get_client_command)
        cursor.execute(get_client_command)
        rows = cursor.fetchall()
        if len(rows) == 0:
            add_client_command = f"INSERT INTO client({client.insert_rows()}) VALUES ({cl.insert()})"
            print(add_client_command)
            cursor.execute(add_client_command)
            client_id = cursor.lastrowid
        else:
            client_id = rows[0][0] #Not sure how to specifically get id in a better way...
        add_job_command = f"INSERT INTO clientrequests(details, stage, client) VALUES (?, ?, ?)"
        cursor.execute(add_job_command, (json.dumps(str(details)), stages.RECEIVED_REQUEST, client_id))
        return cursor.lastrowid


def update_job_stage(job_id:int, new_stage:stages):
    pass

def update_job_receipt(job_id:int, receipt:dict):
    pass 

def get_details(id:int)->dict:
    with sqlite3.connect(SQLDATABASE) as conn:
        cursor = conn.cursor()
        get_job = f"SELECT details FROM clientrequests WHERE id = {id}"
        cursor.execute(get_job)
        row = cursor.fetchone()
        #print(row[0])
        return json.loads(row[0])

def get_user(user_id:int):
    with sqlite3.connect(SQLDATABASE) as conn:
        cursor = conn.cursor()
        #Should change this to be more secure - using the ? and the like
        get_user = f"SELECT * FROM webusers WHERE id = {user_id}"
        response = cursor.execute(get_user).fetchone()
        return User(*response)
    return None


def get_user_by_username(user_name:str):
    with sqlite3.connect(SQLDATABASE) as conn:
        cursor = conn.cursor()
        #Should change this to be more secure - using the ? and the like
        get_user = f"SELECT * FROM webusers WHERE username = '{user_name}'"
        response = cursor.execute(get_user).fetchone()
        print(response)
        return User(*response)
    return None

#Add useful getting functions here
if __name__ == "__main__":
    #a = client()
    #a.email = "Testing"
    #print(add_job({"Sample1": "Result1"}, a))
    print(str(get_details(2)).replace("'", '"'))