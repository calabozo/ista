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


def calc_price(consumption, last_dates, tariff):
    consumption = pd.concat([consumption, last_dates])
    consumption.drop_duplicates(keep="last", inplace=True)
    consumption.sort_values(by=["date"], ascending=False,inplace=True)
    consumption["price"] = 0
    consumption["energy"] = 0
    devices = consumption.serial.unique()
    device_consumption_array = []

    for serial in devices:
        device_consumption = consumption[consumption.serial == serial]
        device_consumption.energy = device_consumption.value.diff(periods=-1)
        device_consumption.price = device_consumption.energy * tariff
        max_date = last_dates.date[last_dates.serial == serial].values
        if len(max_date) > 0:
            device_consumption = device_consumption[device_consumption.date > max_date[0]]
        device_consumption_array.append(device_consumption)
    return pd.concat(device_consumption_array)
