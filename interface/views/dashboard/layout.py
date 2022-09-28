
from dash import html, dcc

from binance import Client
import pandas as pd

coinlist = list(pd.DataFrame(Client().futures_mark_price())['symbol'])

symbol_dropdown = dcc.Dropdown(
    coinlist, id="socket_symbol_dropdown", placeholder="SYMBOL")
interval_dropdown = dcc.Dropdown(
    ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "24h", "1W", "1M"], id="socket_interval_dropdown", placeholder="INTERVAL")

on_off_buttons = html.Div([
    html.Button('Open', id='open-button', className="btn btn-success"),
    html.Button('Close', id='close-button', className="btn btn-danger"),
    html.Div(id="on_off")
])

append_dropdowns = html.Div(
    [symbol_dropdown, interval_dropdown], className="dropdowns")

append = html.Div([
    html.Button('Append', id='append', n_clicks=0,
                className="btn btn-success")
])

delete = html.Div([
    html.Button('Delete', id='delete', n_clicks=0, className="btn btn-danger")
])

append_delete = html.Div([append, delete], className="append-delete")

inputs = html.Div([
    html.H2('Position Config'),
    html.Div(id='position_percentage_out'),
    dcc.Input(id='position_percentage', type='number',
              step="1"),  # position percentage
    html.Div(id='leverage_out'),
    dcc.Input(id='leverage', type='number', step="1"),  # leverage
    html.Div(id='take_out'),
    dcc.Input(id='take', type='number', step="0.1"),  # take profit
    html.Div(id='stop_out'),
    dcc.Input(id='stop', type='number', step="0.1"),  # stop loss
    html.Div(id='max_position_out'),
    dcc.Input(id='max_position', type='number', step="1"),  # max position
    html.H2('Strategy Values'),
    html.Div(id='long_vwap_out'),
    dcc.Input(id='long_vwap', type='number', step="0.001"),  # long vwap,
    html.Div(id='short_vwap_out'),
    dcc.Input(id='short_vwap', type='number', step="0.001"),  # short vwap
    html.Div(id='vwap_period_out'),
    dcc.Input(id='vwap_period', type='number', step="1"),  # vwap period
    html.Div(id='rsi_period_out'),
    dcc.Input(id='rsi_period', type='number', step="1"),  # rsi period
    html.Div(id='rsi_upper_out'),
    dcc.Input(id='rsi_upper', type='number', step="0.1"),  # rsi upper
    html.Div(id='rsi_lower_out'),
    dcc.Input(id='rsi_lower', type='number', step="0.1"),  # rsi lower
], className='inputs')


chart_output = html.Div(id='chart_output')


symbol_dropdown = dcc.Dropdown(
    coinlist, id="symbol_dropdown", placeholder="SYMBOL")
interval_dropdown = dcc.Dropdown(
    ["1m", "3m", "5m", "15m"], id="interval_dropdown", placeholder="INTERVAL")

dropdowns = html.Div([symbol_dropdown, interval_dropdown],
                     className="dropdowns")

rsi = html.Div(
    [html.Div([html.Span(['RSI Parameters'],
                         className="input-group-text"),
               dcc.Input(id='rsi_l', placeholder='period', type='number', step="1")],
              className="input-group-prepend")],
    className="input-group")

vwap = html.Div(
    [html.Div([html.Span(['VWAP Parameters'],
                         className="input-group-text"),
               dcc.Input(id='vwap_l', placeholder='period', type='number'),
               dcc.Input(id='vwap_short', placeholder='long sensivity',
                         type='number', step="0.01"),
               dcc.Input(id='vwap_long', placeholder='short sensivity', type='number', step="0.01")],
              className="input-group-prepend")],
    className="input-group")

layout = html.Div([

    dcc.Interval(id='interval-component',
                 interval=1000,  # in milliseconds (1 seconds)
                 n_intervals=0
                 ),
    on_off_buttons,

    html.Div(id='out'),

    html.Hr(),

    append_dropdowns,
    append_delete,
    html.Div(id='a_d_out'),
    html.Hr(),

    inputs,


    html.Hr(),
    vwap,
    rsi,
    dropdowns,
    chart_output
],

    className="col text-center header-center")
