from requests import request as req
from json import loads

BASE: str = "http://127.0.0.1:80/api"


def request(api: str, method: str, value: str = '', **kwargs):
    url = f'{BASE}{api}{value}'
    response = req(method, url=url, **kwargs).text
    return loads(response)
