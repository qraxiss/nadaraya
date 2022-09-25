from binance.helpers import round_step_size
from logic.exchange import int_to_interval
from helpers import err_return
from threading import Thread
from api import request

from binance.client import Client
from json import dumps


class Order:
    def __init__(self, params, resources) -> None:
        if resources.config['run']:
            self.step_info = resources.step_info
            self.positions = resources.positions
            self.balance = resources.balance
            self.default = resources.default
            self.client: Client = resources.client
            self.config = resources.config
            self.success = False
            self.params = params
            self.orders = None
            self.order = None

            self.params['price'] = float(self.params['price'])

            symbol, interval = self.params['pair'].lower().replace('perp', '').split('@')
            
            interval =  int_to_interval(interval)

            self.pair = symbol + '@kline_' + interval
            self.params['pair'] = self.pair

            self.side = self.params['side']
            self.symbol = symbol.upper()
            self.mode_params = self.default['mode_params']['HEDGE']

            self.params['stop_loss'] = self.config['stop_loss']
            self.params['take_profit'] = self.config['take_profit']

            # so as not to calculate in vain if the trade order is not valid.
            self.order = self.is_order_valid()
            if self.order != False:
                self.client.futures_change_leverage(symbol=self.symbol, leverage=self.config['leverage'])
                # prepare params for the order
                self.levels()
                self.quantity()
                self.round()
                self.common_params = dict(
                    symbol=self.symbol, quantity=str(self.params['quantity']))

                if self.order == 'new':
                    self.new_order()
                elif self.order == 'close':
                    self.close_order()
        else:
            self.success = False

    def is_order_valid(self):
        if self.params['pair'] not in self.positions:
            if self.balance['available'] > (self.config['position_percentage']/100)*self.balance['total']:
                if self.config['max_position'] > len(self.positions):
                    return 'new'

        else:
            if self.side != self.positions[self.pair]['side']:
                return 'close'

        return False

    def levels(self):
        if self.params['side'] == 'BUY':
            self.params['stop_loss'] = (
                1 - (self.params['stop_loss']/100)) * self.params['price']
            self.params['take_profit'] = (
                1 + (self.params['take_profit']/100)) * self.params['price']

        else:
            self.params['stop_loss'] = (1 +
                                        (self.params['stop_loss']/100)) * self.params['price']
            self.params['take_profit'] = (1 -
                                          (self.params['take_profit']/100)) * self.params['price']

    def quantity(self):
        self.params['quantity'] = (self.config['leverage'] * self.balance['total']) * (
            self.config['position_percentage']/100) / self.params['price']

    def round(self):
        steps = self.step_info[self.symbol]

        self.params['quantity'] = round_step_size(
            self.params['quantity'], steps['min_qty'])
        self.params['stop_loss'] = round_step_size(
            self.params['stop_loss'], steps['tick_size'])
        self.params['take_profit'] = round_step_size(
            self.params['take_profit'], steps['tick_size'])

    def new_order(self):

        self.sl_params = dict(**self.mode_params[f'{self.side}_STOP_LOSS'],
                              stopPrice=str(self.params['stop_loss']),
                              **self.common_params)
        self.tp_params = dict(**self.mode_params[f'{self.side}_TAKE_PROFIT'],
                              stopPrice=str(self.params['take_profit']),
                              **self.common_params)
        position_params = dict(**self.mode_params[f'{self.side}'])

        self.stops = [self.sl_params, self.tp_params]

        self.orders = self.client.futures_place_batch_order(
            batchOrders=self.stops)

        # check orders succesfuly opens
        self.telegram_text = ""
        if 'code' in self.orders[0] and 'code' in self.orders[1]:
            self.telegram_text += f'sl_err: {self.orders[0]["msg"]}'
            self.telegram_text += f'tp_err: {self.orders[1]["msg"]}'
        elif 'code' not in self.orders[0] and 'code' in self.orders[1]:
            self.telegram_text += f'tp_err: {self.orders[1]["msg"]}'
            self.client.futures_cancel_order(
                symbol=self.symbol, orderId=self.orders[0]['orderId'])
        elif 'code' in self.orders[0] and 'code' not in self.orders[1]:
            self.telegram_text += f'sl_err: {self.orders[0]["msg"]}'
            self.client.futures_cancel_order(
                symbol=self.symbol, orderId=self.orders[1]['orderId'])
        else:
            try:
                self.position = self.client.futures_create_order(
                    **position_params, **self.common_params)
            except Exception as err:
                self.telegram_text = f'position_err: {err_return(str(type(err)))}'
                self.client.futures_cancel_all_open_orders(symbol=self.symbol)
            else:
                self.success = True
                self.telegram_text = f'pair:{self.pair}\nprice:{self.params["price"]}\nside:{self.side}'

        request('/telegram', 'post', json=dict(text=self.telegram_text))

    def close_order(self):
        close_params = self.mode_params[f'{self.side}_CLOSE']
        self.orders = dict(close_order=self.client.futures_create_order(
            **self.common_params, **close_params))
        try:
            self.client.futures_cancel_order(
                symbol=self.symbol, orderId=self.positions[self.pair]['take_id'])
            self.client.futures_cancel_order(
                symbol=self.symbol, orderId=self.positions[self.pair]['stop_id'])
        except Exception as err:
            self.telegram_text = f'cancel_err: {err_return(str(type(err)))}'
        else:
            self.success = True
            self.telegram_text = f'closed: {self.pair}\n market: MARKET'
        
        request('/telegram', 'post', json=dict(text=self.telegram_text))


class OrderManagement(Order):
    def __init__(self, params, resources) -> None:
        super().__init__(params, resources)

        if self.success:
            if self.order == 'new':
                self.put_order()

            if self.order == 'close':
                self.delete_order()

    def put_order(self):
        position = dict(
            side=self.side,
            price=self.params['price'],
            quantity=self.params['quantity'],
            id=self.position['orderId'],
            positionSide=self.position['positionSide'],
            stop_id=self.orders[0]['orderId'],
            stop_price=self.orders[0]['stopPrice'],
            take_id=self.orders[1]['orderId'],
            take_price=self.orders[1]['stopPrice']
        )

        json = dict(pair=self.pair, position=position)
        request(api='/positions', method='put', json=json)

    def delete_order(self):
        position_data = dict(
            pair=self.pair)

        Thread(target=request, kwargs=dict(api='/positions',
               method='delete', json=position_data)).start()
