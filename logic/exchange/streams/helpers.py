from threading import Thread
from api import request
import pandas as pd
import numpy as np


def find_order_by_id(market, id, df):
    order_type = market[:4].lower() + '_id'  # tp or sl
    result_query = df[df[f'{order_type}'] == id]
    if len(result_query) == 1:
        return result_query.index[0]


def kline_update(stream_json: dict) -> dict:
    kline = stream_json['data']['k']
    kline = np.array(list(kline.values()))[
        [0, 6, 8, 9, 7, 10, 1, 13, 11, 14, 15, 16]].tolist()

    if stream_json['data']['k']['x']:
        closed = True
    else:
        closed = False

    socket = stream_json['stream']

    json = dict(
        closed=closed,
        kline=kline
    )

    request('/klines', 'put', value=f'/{socket}', json=json)


def order_update(order: dict):
    order = order['o']
    if order['X'] == 'FILLED':
        if order['ot'] == 'TAKE_PROFIT_MARKET' or order['ot'] == 'STOP_MARKET':
            data = request('/positions', 'get')
            if data['outcome']:
                positions = data['data']
                df = pd.DataFrame(positions).T
                pair = find_order_by_id(order['ot'], order['i'], df)
                if pair != None:
                    request('/positions', 'delete', json=dict(pair=pair))
                    telegram_text = f'closed :{pair}\nmarket :{order["ot"]}'
                    request('/telegram', json=dict(text=telegram_text))

def account_update(account: dict):
    account = account['a']
    # if float(account['B'][0]['bc']) != 0:
    balance = dict(total=float(account['B'][0]['wb']),
                available=float(account['B'][0]['cw']))
    request('/balance', 'put', json=balance)
    