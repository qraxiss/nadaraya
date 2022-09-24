from interface.views.dashboard.figures import create_chart
from dash import Input, Output, State, dcc, ctx, html
from interface.controllers import is_plot
from api import request

from time import sleep

def init_callbacks(dash_app):
    @dash_app.callback(
        Output('chart_output', 'children'),

        Input('interval-component', 'n_intervals'),
        Input('interval_dropdown', 'value'),
        Input('symbol_dropdown', 'value'),
        Input('vwap_short', 'value'),
        Input('vwap_long', 'value'),
        Input('vwap_l', 'value'),
        Input('rsi_l', 'value'),

    )
    def chart(n, interval, symbol, vwap_short, vwap_long, vwap_l, rsi_l):
        data = is_plot(symbol, interval)
        if not not data:
            fig = create_chart(symbol, interval, data,
                               vwap_short, vwap_long, rsi_l, vwap_l)
            return dcc.Graph(id="graph", figure=fig)
        else:
            return None


    @dash_app.callback(
        Output('out', 'children'),
        Input('append', 'n_clicks'),
        Input('delete', 'n_clicks'),
        Input('socket_symbol_dropdown', 'value'),
        Input('socket_interval_dropdown', 'value')
    )
    def add(n_clicks, n_clicks_2, symbol, interval):
        if symbol != None and interval != None:
            if "append" == ctx.triggered_id:
                r = request('/websocket', 'post', json=dict(pair=symbol.lower() + '@kline_' + interval))
                return r['outcome']

            elif "delete" == ctx.triggered_id:
                r = request('/websocket', 'delete', json=dict(pair=symbol.lower() + '@kline_' + interval))
                return r['outcome']

        return None


    @dash_app.callback(
        Output('a_d_out', 'children'),
        Input('append', 'n_clicks'),
        Input('delete', 'n_clicks')
    )
    def pairs(a,d):
        sleep(4)
        response = request('/websocket', 'get')
        if response['outcome']:
            pairs = list()
            for pair in response['data']:
                pairs.append(html.Div(pair))

            return html.Div(pairs)

    @dash_app.callback(
        Output('on_off', 'children'),
        Input('open-button', 'n_clicks'),
        Input('close-button', 'n_clicks'))
    def on_off(open, close):
        if "open-button" == ctx.triggered_id:
            request('/config', 'put', json=dict(key='run', value=True))
            return 'Opened'

        elif "close-button" == ctx.triggered_id:
            request('/config', 'put', json=dict(key='run', value=False))
            return 'Closed'

        else:
            r=request('/config', 'get', json=dict(key='run'))
            if r['outcome']:
                if r['data']:
                    return 'Open'

                else:
                    return 'Not open'

    dash_app = init_inputs(dash_app=dash_app)

    return dash_app


def init_inputs(dash_app):
    @dash_app.callback(
        Output('position_percentage_out', 'children'),
        Input('position_percentage', 'value')
    )
    def percentage(value):
        if value != None:
            response = request(
                '/config', 'put', json=dict(key='position_percentage', value=value))
        value = request('/config', 'get',
                        json=dict(key='position_percentage'))['data']
        return f'Position Percentage: {value}'

    @dash_app.callback(
        Output('leverage_out', 'children'),
        Input('leverage', 'value')
    )
    def leverage(value):
        if value != None:
            response = request(
                '/config', 'put', json=dict(key='leverage', value=value))
        value = request('/config', 'get',
                        json=dict(key='leverage'))['data']
        return f'Leverage: {value}'

    @dash_app.callback(
        Output('take_out', 'children'),
        Input('take', 'value')
    )
    def take(value):
        if value != None:
            response = request(
                '/config', 'put', json=dict(key='take_profit', value=value))
        value = request('/config', 'get',
                        json=dict(key='take_profit'))['data']
        return f'Take Profit: {value}'

    @dash_app.callback(
        Output('stop_out', 'children'),
        Input('stop', 'value')
    )
    def stop(value):
        if value != None:
            response = request(
                '/config', 'put', json=dict(key='stop_loss', value=value))
        value = request('/config', 'get',
                        json=dict(key='stop_loss'))['data']
        return f'Stop Loss: {value}'

    @dash_app.callback(
        Output('max_position_out', 'children'),
        Input('max_position', 'value')
    )
    def max_position(value):
        if value != None:
            response = request(
                '/config', 'put', json=dict(key='max_position', value=value))
        value = request('/config', 'get',
                        json=dict(key='max_position'))['data']
        return f'Max Position: {value}'

    # @dash_app.callback(
    #     Output('long_vwap_out', 'children'),
    #     Input('long_vwap', 'value')
    # )
    # def long_vwap(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='vwap_sensitivity_long', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='vwap_sensitivity_long'))['data']
    #     return f'Vwap Long Value: {value}'

    # @dash_app.callback(
    #     Output('short_vwap_out', 'children'),
    #     Input('short_vwap', 'value')
    # )
    # def short_vwap(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='vwap_sensitivity_short', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='vwap_sensitivity_short'))['data']
    #     return f'Vwap Short Value: {value}'

    # @dash_app.callback(
    #     Output('vwap_period_out', 'children'),
    #     Input('vwap_period', 'value')
    # )
    # def vwap_period(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='vwap_period', value=value))
    #     value = request('/strategy', 'get',
    #          response = request(
    #             '/strategy', 'put', json=dict(key='vwap_period', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='vwap_period'))['data']
    #     return f'Vwap Period: {value}'

    # @dash_app.callback(
    #     Output('rsi_period_out', 'children'),
    #     Input('rsi_period', 'value')
    # )
    # def rsi_period(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_period', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_period'))['data']
    #     return f'Rsi Period: {value}'

    # @dash_app.callback(
    #     Output('rsi_upper_out', 'children'),
    #     Input('rsi_upper', 'value')
    # )
    # def rsi_upper(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_long_level', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_long_level'))['data']
    #     return f'Rsi Long Level: {value}'

    # @dash_app.callback(
    #     Output('rsi_lower_out', 'children'),
    #     Input('rsi_lower', 'value')
    # )
    # def rsi_lower(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_short_level', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_short_level'))['data']
    #     return f'Rsi Long Level: {value}'
    # @dash_app.callback(
    #     Output('rsi_period_out', 'children'),
    #     Input('rsi_period', 'value')
    # )
    # def rsi_period(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_period', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_period'))['data']
    #     return f'Rsi Period: {value}'

    # @dash_app.callback(
    #     Output('rsi_upper_out', 'children'),
    #     Input('rsi_upper', 'value')
    # )
    # def rsi_upper(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_long_level', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_long_level'))['data']
    #     return f'Rsi Long Level: {value}'

    # @dash_app.callback(
    #     Output('rsi_lower_out', 'children'),
    #     Input('rsi_lower', 'value')
    # )
    # def rsi_lower(value):
    #     if value != None:
    #         response = request(
    #             '/strategy', 'put', json=dict(key='rsi_short_level', value=value))
    #     value = request('/strategy', 'get',
    #                     json=dict(key='rsi_short_level'))['data']
    #     return f'Rsi Long Level: {value}'
    return dash_app
