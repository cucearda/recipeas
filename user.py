from flask import current_app
from flask_login import UserMixin
import psycopg2

class User(UserMixin):
    def __init__(self, userid,username, password):
        self.userid = userid
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(user_name):
    conn = psycopg2.connect(dbname= "recipeas2", user="postgres", host='localhost', password= "arda")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM  users 
                WHERE username= (%s)""", (user_name,))
    tup = cur.fetchone()
    
    user = User(tup[0], tup[1], tup[2]) if tup else None
    if user is not None:
        return user
        
    else:
        print("USER NOT FOUND")
    
    return user