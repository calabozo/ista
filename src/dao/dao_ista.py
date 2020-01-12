import psycopg2
import psycopg2.extras
import logging


class DaoIsta(object):
    def __init__(self,user,password,host,port=5432,database='ista'):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database


    def connect(self):
        self.conn = psycopg2.connect(user=self.user, password=self.password, host=self.host,
                                     port=self.port, dbname=self.database)

    def disconnect(self):
        self.conn.close()

    def get_last_lecture_for_device(self,serial):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT max(date) from ista_measure where serial=%s;", (serial,))
        max_date = cur.fetchone()
        cur.close()
        if len(max_date)>0:
            max_date = max_date[0]
        return max_date

    def insert_value(self,serial,date,value):
        sql = "INSERT INTO ista_measure (serial, date, value) VALUES (%s,%s, %s)"
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql, (serial,date,value))
        logging.debug("Inserted entry for device:%s", serial)
        self.conn.commit()
        cur.close()

    def get_all_devices(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from ista_devices;")
        devices = cur.fetchall()
        cur.close()
        return devices
