#!/usr/bin/python3
import requests
import logging
import pandas as pd

#https://oficina.ista.es/GesCon/GestionFincas.do?d-4360165-e=2&metodo=listadoLecturasRadio&metodo=preCargaLecturasRadio&metodo=listadoLecturasRadio&6578706f7274=1
#https://oficina.ista.es/GesCon/GestionFincas.do?d-4360165-e=2&metodo=listadoLecturasRadio&metodo=preCargaLecturasRadio&metodo=listadoLecturasRadio&6578706f7274=1
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

def login_ista(user,password):

    session = requests.Session()

    host='oficina.ista.es'
    url_main = f"https://{host}/GesCon/MainPageAbo.do"
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language':'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip,deflate,br',
               'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
               'Content-Type':"application/x-www-form-urlencoded",
               'Origin':f'https://{host}',
     #          'Upgrade-Insecure-Requests':'1',
     #          'DNT':'1',
               'Referer':url_main}
    r = checkrequest(session.get)(url_main, headers=headers, verify=False)


    url = f"https://{host}/GesCon/GestionOficinaVirtual.do"
    r = checkrequest(session.post)(f'{url};jsessionid={session.cookies.get("JSESSIONID")}',
                         headers=headers,
                         data={'metodo': 'loginAbonado', 'loginName': user, 'password': password},
                         verify=True)

    if r.text.find("Mis recibos")>0:
        return session
    else:
        return None

def get_readings(session):
    host = 'oficina.ista.es'
    url_readings='https://oficina.ista.es/GesCon/GestionFincas.do?metodo=preCargaLecturasRadio'
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip,deflate,br',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
               'Content-Type': "application/x-www-form-urlencoded",
               'Origin': f'https://{host}'}
    r = checkrequest(session.get)(url_readings, headers=headers, verify=False)
    tables = pd.read_html(r.text)
    consumption  = tables[1]
    print(r.text)



