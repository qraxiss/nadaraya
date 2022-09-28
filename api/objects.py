from logic import OrderManagement, Strategy, cancel_levels, change_margin_config
from helpers import err_return, send_telegram_messages, socket_parser
from data.access import set_config, set_values
from api.base import BaseApi


class Klines(BaseApi):
    def get(self, pair):
        try:
            self.json['data'] = self.resources.klines[pair][-self.data['limit']:]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False
        return self.json

    def post(self, pair):
        try:
            self.resources.klines[pair] = self.data
            self.resources.strategy[pair] = Strategy(
                values=self.resources.values, pair=pair,
                config=self.resources.config, default=self.resources.default)
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def delete(self, pair):
        try:
            del self.resources.klines[pair]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def put(self, pair):
        try:
            if self.data['closed']:
                del self.resources.klines[pair][0]
                self.resources.klines[pair].append(self.data['kline'])
                self.resources.strategy[pair].signal(
                    self.resources.klines[pair])
            else:
                self.resources.klines[pair][-1] = self.data['kline']

            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Strategyy(BaseApi):
    def get(self):
        try:
            if self.data == None:
                self.json['data'] = self.resources.values
            else:
                self.json['data'] = self.resources.values[self.data['key']]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def put(self):
        try:
            self.resources.values[self.data['key']] = self.data['value']
            set_values(self.resources.values)

            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Config(BaseApi):
    def get(self):
        try:
            if self.data == None:
                self.json['data'] = self.resources.config
            else:
                self.json['data'] = self.resources.config[self.data['key']]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def put(self):
        try:
            self.resources.config[self.data['key']] = self.data['value']
            set_config(self.resources.config)

            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Positions(BaseApi):
    def get(self):
        try:
            self.json['data'] = self.resources.positions
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def put(self):
        try:
            self.resources.positions[self.data['pair']] = self.data['position']
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def delete(self):
        try:
            cancel_levels(self.resources.client,
                          self.data['pair'], self.resources.positions)
            del self.resources.positions[self.data['pair']]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Balance(BaseApi):
    def get(self):
        try:
            self.json['data'] = self.resources.balance
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def put(self):
        try:
            self.resources.balance['total'] = self.data['total']
            self.resources.balance['available'] = self.data['available']
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Default(BaseApi):
    def get(self):
        try:
            self.json['data'] = self.resources.default[self.data['key']]
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Order(BaseApi):
    def post(self):
        order = OrderManagement(params=self.data, resources=self.resources)


class WebsocketManage(BaseApi):
    def post(self):
        try:
            self.resources.websocket.kline_thread(socket=self.data['pair'])
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def delete(self):
        try:
            self.resources.websocket.kline_close(self.data['pair'])
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


    def get(self):
        try:
            self.json['data'] = self.resources.websocket.get_sockets()
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class UserSocketManage(BaseApi):
    def post(self):
        try:
            self.resources.websocket.user_thread(
                account=self.resources.default['account'])
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json

    def delete(self):
        try:
            self.resources.websocket.user_close()
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False

        return self.json


class Telegram(BaseApi):
    def post(self):
        try:
            send_telegram_messages(
                self.resources.default['telegram'], self.data['text'])
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False


class MarginConfig(BaseApi):
    def put(self):
        if 'symbol' in self.data:
            change_margin_config(self.resources.client,
                                 self.data['symbol'],
                                 self.data['leverage'],
                                 self.data['margin_type'])
        else:
            for kline in self.resources.klines:
                symbol, interval = socket_parser(kline)
                change_margin_config(self.resources.client,
                                     symbol,
                                     self.data['leverage'],
                                     self.data['margin_type'])


class OnOff(BaseApi):
    def put(self):
        try:
            self.resources.run = self.data['run']
            self.json['outcome'] = True
        except Exception as err:
            self.json['err'] = err_return(str(type(err)))
            self.json['outcome'] = False
