from dao.dao_ista import DaoIsta
import configparser
import datetime
import pandas as pd


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
    assert dao.get_last_lecture_for_device('902358070') == datetime.date(2019, 10, 3)
    assert dao.get_last_lecture_for_device('406805810') == datetime.date(2019, 10, 2)
    assert dao.get_last_lecture_for_device('111111111') is None
    dao.disconnect()


def test_insert():
    dao = _get_dao()
    date = pd.Timestamp('2020-01-08 00:00:00')
    dao.insert_value('222222', date, 32)
    assert dao.get_last_lecture_for_device('222222') == datetime.date(2020, 1, 8)
    dao.disconnect()
