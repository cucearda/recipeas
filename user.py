from flask import current_app
from flask_login import UserMixin
import psycopg2
import dbcredentials as cred
class User(UserMixin):
    def __init__(self, userid, username, password, nickname, date, karma, is_admin):
        self.userid = userid
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = is_admin
        self.nickname = nickname
        self.register_date = date
        self.karma = karma

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active

def get_user(user_name):
    conn = psycopg2.connect(dbname= cred.dbname, user=cred.user, host=cred.host, password= cred.password)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM  users 
                WHERE username= (%s)""", (user_name,))
    tup = cur.fetchone()
    
    user = User(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6]) if tup else None
    if user is not None:
        return user
        
    else:
        print("USER NOT FOUND")
    
    return user
def get_user_by_id(user_id):
    conn = psycopg2.connect(dbname= cred.dbname, user=cred.user, host=cred.host, password= cred.password)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM  users 
                WHERE id= (%s)""", (user_id,))
    tup = cur.fetchone()
    
    user = User(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6]) if tup else None
    if user is not None:
        return user
        
    else:
        print("USER NOT FOUND")
    
