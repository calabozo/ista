from ista.ista import Ista
import sslkeylog
import configparser
import pandas as pd


def test_login_no_ok():
    sslkeylog.set_keylog("sslkeylog.txt")
    ista = Ista("XXX","XXX")
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
    assert data.shape[1] == 15
    values = ista.clean_data(data)
    assert values.value.mean() > 0
    assert values.date.max() == pd.Timestamp('2020-01-08 00:00:00')
