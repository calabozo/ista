from ista.ista import Ista
from device import calc_price
import sslkeylog
import configparser
import pandas as pd


def test_login_no_ok():
    sslkeylog.set_keylog("sslkeylog.txt")
    ista = Ista("XXX", "XXX")
    out = ista.login_ista()
    assert out is False


def test_login_ok():
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['ISTA']['user']
    password = config['ISTA']['password']
    sslkeylog.set_keylog("sslkeylog.txt")

    ista = Ista(user, password)
    out = ista.login_ista()
    assert out is True
    data = ista.get_readings()
    assert data.value.mean() > 0
    assert data.date.max() == pd.Timestamp('2020-01-08 00:00:00')
    assert data.columns.values.tolist() == ['serial', 'date', 'value']


def test_calc_price():
    serial1 = '11111'
    serial2 = '22222'
    serial3 = '33333'
    day1 = pd.Timestamp('2020-01-01')
    day2 = pd.Timestamp('2020-01-02')
    day3 = pd.Timestamp('2020-01-03')
    consumption = pd.DataFrame({'serial': [serial1, serial1, serial1, serial2, serial2, serial2, serial3, serial3],
                                'date': [day1, day2, day3, day1, day2, day3, day1, day2],
                                'value': [10, 11, 12, 30, 30.5, 40, 21, 22]
                                })

    last_day1 = pd.Timestamp('2019-12-31')
    last_day2 = pd.Timestamp('2020-01-01')
    last_date = pd.DataFrame({'serial': [serial1, serial2],
                                'date': [last_day1, last_day2],
                                'value': [7, 28]
                                })
    tariff = 2
    price_consumption = calc_price(consumption,last_date,tariff)
    assert price_consumption.price.mean() > 0
    assert price_consumption.energy.mean() > 0
    con = price_consumption[price_consumption.serial == serial1]
    assert con.energy[con.date == day3].values.tolist() == [1]
    assert con.energy[con.date == day2].values.tolist() == [1]
    assert con.energy[con.date == day1].values.tolist() == [3]
    assert con.price[con.date == day1].values.tolist() == [6]
    con = price_consumption[price_consumption.serial == serial2]
    assert con.energy[con.date == day3].values.tolist() == [9.5]
    assert con.energy[con.date == day2].values.tolist() == [0.5]
    assert len(con.energy[con.date == day1].values) == 0

