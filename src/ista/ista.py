#!/usr/bin/python3
import requests
import logging
import pandas as pd
from datetime import date

def checkrequest(func):
    def wrapper(*args, **kwargs):
        try:
            r=func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logging.error("Request timeout")
            return None
        except Exception as err:
            logging.error(f"{str(err)}")
            return None
        if r.status_code != 200:
            logging.error(f"The request returned status code {r.status_code}")
            logging.error(r.headers())
            logging.error(r.text)
            return None
        if r.status_code != 200:
            logging.error(f"The request returned status code {r.status_code}")
            logging.error(r.headers())
            logging.error(r.text)
            return None

        return r
    return wrapper

class Ista(object):
    def __init__(self,user,password):
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.host = 'oficina.ista.es'
        self.url_main = f"https://{self.host}/GesCon/MainPageAbo.do"
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language':'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip,deflate,br',
                   'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
                   'Content-Type':"application/x-www-form-urlencoded",
                   'Origin':f'https://{self.host}',
                   'Referer':self.url_main}

    def login_ista(self):

        r = checkrequest(self.session.get)(self.url_main, headers=self.headers, verify=False)
        if r is None:
            return False

        url = f"https://{self.host}/GesCon/GestionOficinaVirtual.do"
        r = checkrequest(self.session.post)(f'{url};jsessionid={self.session.cookies.get("JSESSIONID")}',
                             headers=self.headers,
                             data={'metodo': 'loginAbonado', 'loginName': self.user, 'password': self.password},
                             verify=True)
        if r is None:
            return False

        if r.text.find("Mis recibos")>0:
            return True
        else:
            return False

    def get_readings(self):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip,deflate,br',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
                   'Content-Type': "application/x-www-form-urlencoded",
                   'Origin': f'https://{self.host}'}
        url_readings='https://oficina.ista.es/GesCon/GestionFincas.do?metodo=preCargaLecturasRadio'
        r = checkrequest(self.session.get)(url_readings, headers=headers, verify=False)
        if r is not None and r.text.find("Acceso a la Oficina Virtual")<0:
            tables = pd.read_html(r.text)
            consumption = tables[1]
            return consumption
        else:
            return None

    def clean_data(self,data):
        cols = data.columns
        col_serie = cols[2]
        cols_values = cols[4:]
        values = pd.melt(data, id_vars=[col_serie], value_vars=cols_values)
        values["date_str"] = values.variable+f"/{date.today().year}"
        values["date"] = pd.to_datetime(values["date_str"],format="%d/%m/%Y")
        idx=values.date - pd.Timestamp.now() > pd.Timedelta(value="0")
        values.date[idx] = values.date[idx]-pd.DateOffset(years=1)
        values = values.rename(columns={'Nº serie':'serial'})[['serial','date','value']]
        return values