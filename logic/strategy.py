from binance.helpers import round_step_size
from helpers import socket_parser
from data.access import get_vwap
from statistics import stdev
from api import request
import pandas_ta as ta
from json import loads
import pandas as pd
import requests


class Strategy:
    def __init__(self, values: dict, pair: dict, config: dict, default: dict) -> None:
        self.vwap_df = pd.DataFrame(get_vwap())
        self.default = default
        self.values = values
        self.config = config
        self.pair = pair

        self.is_liq, self.is_rsi, self.is_vwap = None, "Not Calculated", "Not Calculated"

        # coin glass
        symbol = socket_parser(pair)[0].replace('USDT', '')
        self.headers = {
            'coinglassSecret': 'e5e725f31155429aaca9071d01641958'
        }
        self.url = f"https://open-api.coinglass.com/api/pro/v1/futures/liquidation/detail/chart?symbol={symbol}&timeType=9"

# RSI
    def calc_rsi(self):
        self.rsi = ta.rsi(self.klines[4], length=self.values['rsi_period'])

    def check_rsi(self):
        self.calc_rsi()
        if self.values['rsi_long_level'] < self.rsi[-1]:
            self.is_rsi = 'SELL'

        elif self.values['rsi_short_level'] > self.rsi[-1]:
            self.is_rsi = 'BUY'

        else:
            self.is_rsi = 'No signal'


# Liqudation


    def check_liq(self):
        self.calc_liq()
        self.get_liq()
        if self.actual_liq_value > self.vwap_liq_value:
            self.is_liq = True

    def calc_liq(self):
        c = list()  # changes
        for i in range(-1, -6, -1):
            c.append((self.klines[4][i-1]-self.klines[4][i])/self.klines[4][i])
        d1 = stdev(c) * 130 * self.values['vwap_sensitivity_long']*1.2
        d2 = stdev(c) * 130 * self.values['vwap_sensitivity_short']*1.2
        direction = (sum(c))*10+1
        self.long = d1+(1-direction)
        self.short = d2-(1-direction)

        max_vwap = max(self.short, self.long)
        max_vwap = round_step_size(max_vwap, 0.01)

        self.vwap_liq_value = int(
            self.vwap_df[self.vwap_df['VWAPLong'] == max_vwap]['Liquidation'])

    def get_liq(self):
        response = requests.request("GET", self.url, headers=self.headers).text
        liq = loads(response)['data'][-1]
        self.actual_liq_value = liq['buyVolUsd'] + liq['sellVolUsd']

# Vwap
    def calc_vwap(self):
        self.vwap = ta.vwap(high=self.klines[2], low=self.klines[3],
                            close=self.klines[4], volume=self.klines[5],
                            anchor="min", length=self.values['vwap_period'])
        self.vwap_upper = self.vwap * 1-(self.long/100)
        self.vwap_short = self.vwap * 1+(self.long/100)

    def check_vwap(self):
        self.calc_vwap()
        if self.vwap_upper[-1] < self.klines[4].iloc[-1]:
            self.is_vwap = 'SELL'
        elif self.vwap_short[-1] > self.klines[4].iloc[-1]:
            self.is_vwap = 'BUY'
        else:
            self.is_vwap = 'No signal'


# Candle
    def check_candle(self):
        if self.klines[4].iloc[-1] > self.klines[1].iloc[-1]:
            self.is_candle = "SELL"
        elif self.klines[4].iloc[-1] < self.klines[1].iloc[-1]:
            self.is_candle = "BUY"

# Methods

    def change(self, key, value):
        self.values[key] = value

    def signal(self, klines):
        self.klines = pd.DataFrame(klines)
        self.klines[[1, 2, 3, 4, 5]] = self.klines[[
            1, 2, 3, 4, 5]].astype(float)
        self.klines.index = pd.to_datetime(self.klines[0], unit='ms')

        self.check_liq()
        if self.is_liq:
            self.check_rsi()
            self.check_vwap()
            # self.check_candle()

            if self.is_rsi != None:
                if self.is_vwap == self.is_rsi:
                    request('/order', 'post', json=dict(
                        pair=self.pair,
                        stop_loss=self.config['stop_loss'],
                        take_profit=self.config['take_profit'],
                        price=self.klines[4][-1],
                        side=self.is_rsi
                    ))

        signal_info = f'pair: {self.pair}\nliquidation: {self.is_liq}\nvwap: {self.is_vwap}\nrsi: {self.is_rsi}'
        request('/telegram', 'post', json=dict(text=signal_info))