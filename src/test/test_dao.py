from dao.dao_ista import DaoIsta
import configparser
import datetime
import pandas as pd
import pytest


def _get_dao():
    config = configparser.ConfigParser()
    config.read('config.ini')
    user = config['DB']['user']
    password = config['DB']['password']
    database = config['DB']['database']
    dao = DaoIsta(user=user, password=password, host='127.0.0.1', database=database)
    dao.connect()
    return dao


def test_last_date():
    dao = _get_dao()

    assert dao.get_last_lecture_for_device('902358070') == [3.0, datetime.date(2019, 10, 3)]
    assert dao.get_last_lecture_for_device('406805810') == [1.0, datetime.date(2019, 10, 2)]
    assert dao.get_last_lecture_for_device('111111111') is None
    dao.disconnect()


def test_insert():
    serial = '222222'
    dao = _get_dao()
    dao.remove_all_measures_for_device(serial)

    date = pd.Timestamp('2020-01-08 00:00:00')
    dao.insert_value(serial, date, 32, 1, 10)
    assert dao.get_last_lecture_for_device(serial) == [32, datetime.date(2020, 1, 8)]
    date = pd.Timestamp('2020-01-09 00:00:00')
    dao.insert_value(serial, date, 33, 2, 3)
    assert dao.get_last_lecture_for_device(serial) == [33, datetime.date(2020, 1, 9)]

    dao.remove_all_measures_for_device(serial)
    assert dao.get_last_lecture_for_device(serial) is None
    dao.disconnect()


def test_consumption():
    serial = '123456'
    dao = _get_dao()
    dao.remove_all_measures_for_device(serial)
    dao.insert_value(serial, pd.Timestamp('2019-12-08'), 30.7, 1.8, 3.1)
    dao.insert_value(serial, pd.Timestamp('2019-12-10'), 31, 0.3, 2.1)
    dao.insert_value(serial, pd.Timestamp('2020-01-08'), 32, 1, 10)
    dao.insert_value(serial, pd.Timestamp('2020-01-10'), 35, 3, 10)

    serial_tuple = tuple([serial])
    consumption = dao.get_monthly_consumption(serial_tuple)
    assert len(consumption) == 2
    assert consumption[0].price == 20
    assert consumption[1].price == 5.2
    assert consumption[0].energy == 4
    assert consumption[1].energy == 2.1
    assert consumption[0].month == '2020-01'
    assert consumption[1].month == '2019-12'

    serial2 = '123457'
    dao.remove_all_measures_for_device(serial2)
    dao.insert_value(serial2, pd.Timestamp('2019-11-08'), 30.7, 1.8, 3.1)
    dao.insert_value(serial2, pd.Timestamp('2019-12-10'), 31, 0.3, 2.1)
    dao.insert_value(serial2, pd.Timestamp('2020-01-01'), 32, 3.1, 7.1)
    dao.insert_value(serial2, pd.Timestamp('2020-01-12'), 35, 2.9, 12)

    serial_tuple = tuple([serial, serial2])
    consumption = dao.get_monthly_consumption(serial_tuple)
    assert len(consumption) == 3
    assert consumption[0].price == pytest.approx(20 + 12 + 7.1)
    assert consumption[1].price == pytest.approx(5.2 + 2.1)
    assert consumption[2].price == 3.1

    assert consumption[0].energy == pytest.approx(4 + 3.1 + 2.9)
    assert consumption[1].energy == pytest.approx(2.1 + 0.3)
    assert consumption[2].energy == pytest.approx(1.8)

    assert consumption[0].month == '2020-01'
    assert consumption[1].month == '2019-12'
    assert consumption[2].month == '2019-11'

    dao.remove_all_measures_for_device(serial)
    dao.remove_all_measures_for_device(serial2)
    dao.disconnect()


def test_get_all_devices():
    dao = _get_dao()
    devices = dao.get_all_devices()
    assert len(devices) == 11
    assert devices[0].serial == "902358070"
    assert devices[0].name == "Agua"
    assert devices[0].type == "Agua caliente"
    dao.disconnect()
