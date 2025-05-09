import sqlite3
from enum import IntEnum

sql_database = ""
#Grab the stages from database and throw in dict of {id:name}
# Hmm, I may change how this works later - it would be nice if I could add it dynamically with the database
# But that typically will make it hard to use later - Maybe just a way to check that it's right
class stages(IntEnum):
    RECEIVED_REQUEST = 1
    pass
#This needs to match the values in client database
class client:
    email: str 

    def insert_rows():
        #Probably can make this more efficient at somepoint and then use this for insert - doing it lazy for now
        return f"email"
    
    def to_sql_client(self):
        return f"email = {self.email}"
    
    def insert(self):
        return f"{self.email}"

# Attempts to find client in table, if not found makes one and adds new row to clientrequests
# With no receipt and Stage at RECEIVED_REQUEST
# Return the id of the row entered, or -1 for an error
def add_job(details:dict, cl: client)->int:
    #Should add a try except here
    with sqlite3.connect(sql_database) as conn:
        cursor = conn.cursor()
        get_client_command = f"SELECT * FROM client WHERE {cl.to_sql_client()}"
        cursor.execute(get_client_command)
        rows = cursor.fetchall()
        if len(rows) == 0:
            add_client_command = f"INSERT INTO client({client.insert_rows()}), VALUES ({cl.insert()})"
            cursor.execute(add_client_command)
            client_id = cursor.lastrowid
        else:
            client_id = rows[0][0] #Not sure how to specifically get id in a better way...
        add_job_command = f"INSERT INTO clientrequests(details, stage, client) VALUES (?, ?, ?)"
        cursor.execute(add_job_command, (details, stages.RECEIVED_REQUEST, client_id))
        return cursor.lastrowid


def update_job_stage(job_id:int, new_stage:stages):
    pass

def update_job_receipt(job_id:int, receipt:dict):
    pass 


#Add useful getting functions here
