import psycopg2
import psycopg2.extras
import logging
from ista.device import MonthlyConsumption, Device


class DaoIsta(object):
    def __init__(self, user, password, host, port=5432, database='ista'):
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

    def get_last_lecture_for_device(self, serial):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = "WITH max_date AS (SELECT max(date) as date from ista_measure where serial=%s)" \
              "select value, i.date as date from ista_measure i, max_date where serial=%s and i.date=max_date.date"
        cur.execute(sql, (serial, serial))

        row = cur.fetchone()
        cur.close()
        if row is not None:
            row[0] = float(row[0])
        return row

    def insert_value(self, serial, date, value, energy, price):
        sql = "INSERT INTO ista_measure (serial, date, value, energy, price) VALUES (%s,%s, %s, %s, %s)"
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql, (serial, date, value, energy, price))
        logging.debug("Inserted entry for device:%s", serial)
        self.conn.commit()
        cur.close()

    def get_monthly_consumption(self, serial_numbers):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = "select sum(energy) as energy,sum(price) as price,to_char(date,'YYYY-MM') as month from ista_measure " \
              "where serial in %s group by to_char(date, 'YYYY-MM') order by month desc; "

        cur.execute(sql, (serial_numbers,))
        rows = cur.fetchall()
        cur.close()
        monthly_consumptions = []
        for row in rows:
            monthly_consumptions.append(MonthlyConsumption(row))

        return monthly_consumptions

    def remove_all_measures_for_device(self, serial):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("delete from ista_measure where serial=%s;", (serial,))
        cur.close()

    def get_all_devices(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * from ista_devices;")
        rows = cur.fetchall()
        cur.close()
        devices = []
        for row in rows:
            devices.append(Device(row))
        cur.close()
        return devices
