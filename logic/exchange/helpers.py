from helpers import socket_parser
from binance.client import Client
from threading import Thread
from api import request


def get_step_info(client):
    exchange_info = client.futures_exchange_info()['symbols']
    symbol_info = dict()
    for symbol in exchange_info:
        tick_size = symbol['filters'][0]['tickSize']
        min_qty = symbol['filters'][1]['minQty']
        symbol_info[symbol['symbol']] = {
            'min_qty': min_qty, 'tick_size': tick_size}

    return symbol_info


def get_balance(client):
    balance = client.futures_account_balance()[6]
    return dict(
        total=float(balance['balance']),
        available=float(balance['withdrawAvailable'])
    )


def cancel_levels(client:Client, pair, positions):
    symbol, interval = socket_parser(pair)

    for i in range(5):
        try:
            client.futures_cancel_all_open_orders(symbol=symbol)
            break
        except Exception as e:
            text = f'Açık işlemler kapatılamadı, exception:{e}'
            request('/telegram', 'post', json=dict(text=text))

def change_margin_config(client, symbol, leverage, margin_type):
    Thread(target=client.futures_change_leverage,
            kwargs=dict(symbol=symbol,
                        leverage=leverage)).start()
    Thread(target=client.futures_change_margin_type,
            kwargs=dict(symbol=symbol,
                        marginType=margin_type)).start()


def int_to_interval(interval):
    interval =  int(interval)
    if interval > 60:
        return str(interval/60) + 'm'
    else:
        return str(interval) + 'm'