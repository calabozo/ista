import pandas as pd
class Device(object):
    def __init__(self, row):
        self.serial = row['serial']
        self.name = row['name']
        self.type = row['type']


class MonthlyConsumption(object):
    def __init__(self, row):
        self.energy = float(row['energy'])
        self.price = float(row['price'])
        self.month = row['month']

    def __str__(self):
        out = 'Energy: %s, Price: %s, Month: %s' % (
            str(self.energy), str(self.price), str(self.month))
        return out

def calc_price(consumption,last_dates):

    consumption=pd.concat([consumption,last_dates])
    consumption.drop_duplicates(keep="last",inplace=True)
    consumption.sort_values(by="date")
    consumption["price"]=0
    consumption["price"]= 0
    devices=consumption.serial.unique()
    for serial in devices:
        device_consumption = consumption[consumption.serial == serial]


