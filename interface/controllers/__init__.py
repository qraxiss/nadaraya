from api import request

url = 'http://127.0.0.1:80/api'

def is_plot(symbol, interval):
    if symbol != None and interval != None:
            socket = '/' + symbol.lower() + '@kline_' + interval

            data = request('/klines', 'get', value=socket, json=dict(limit=30))
            if data['outcome']:
                return data
            else:
                return False