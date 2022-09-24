from binance.helpers import round_step_size
import plotly.graph_objects as go
import pandas_ta as ta
import pandas as pd
import statistics


vwap_sensitivity_long = 0.68
vwap_sensitivity_short = 0.90
rsi_l = 7
vwap_l = 6


def create_chart(symbol, interval, data, vwap_long, vwap_short, rsi_l_, vwap_l_):

    func_values = list()
    for func, local in zip([vwap_long, vwap_short, rsi_l_, vwap_l_], [vwap_sensitivity_long, vwap_sensitivity_short, rsi_l, vwap_l]):
        try:
            func = float(func)
        except:
            func = local

        func_values.append(func)

    vwap_long, vwap_short, rsi_l_, vwap_l_ = func_values

    df = pd.DataFrame(data['data'])
    df[[0, 1, 2, 3, 4, 5]] = df[[0, 1, 2, 3, 4, 5]].astype('float')
    df[0] = pd.to_datetime(df[0], unit='ms')
    df.index = df[0]

    vwap = ta.vwap(high=df[2], low=df[3], close=df[4],
                   volume=df[5], length=vwap_l_, anchor="min")

    rsi = ta.rsi(df[2], rsi_l_)

    c1 = (
        ((float(df[4][-2])-float((df[4][-1])))/float(df[4][-1])))
    c2 = (
        ((float(df[4][-3])-float((df[4][-2])))/float(df[4][-2])))
    c3 = (
        ((float(df[4][-4])-float((df[4][-3])))/float(df[4][-3])))
    c4 = (
        ((float(df[4][-5])-float((df[4][-4])))/float(df[4][-4])))
    c5 = (
        ((float(df[4][-6])-float((df[4][-5])))/float(df[4][-5])))

    d1 = (statistics.stdev([c1, c2, c3, c4, c5])) * \
        130*float(vwap_long)*1.2
    d2 = (statistics.stdev([c1, c2, c3, c4, c5])) * \
        130*float(vwap_short)*1.2
    direction = (c1+c2+c3+c4+c5)*10+1
    long = d1+(1-direction)
    short = d2-(1-direction)

    vwaplong = vwap*(1-(long/100))
    vwapshort = vwap*(1+(short/100))

    set1 = {
        'x': df[0],
        'open': df[1],
        'high': df[2],
        'low': df[3],
        'close': df[4],
        'type': 'candlestick',
        'name': 'candlestick'
    }

    set2 = {
        'x': df[0],
        'y': vwap,
        'type': 'scatter',
        'mode': 'lines',
        'line': {
            'width': 1,
            'color': 'blue'
        },
        'name': 'VWAP'
    }

    set3 = {
        'x': df[0],
        'y': vwaplong,
        'type': 'scatter',
        'mode': 'lines',
        'line': {
            'width': 1,
            'color': 'green'
        },
        'name': 'VWAP Long'
    }

    set4 = {
        'x': df[0],
        'y': vwapshort,
        'type': 'scatter',
        'mode': 'lines',
        'line': {
            'width': 1,
            'color': 'red'
        },
        'name': 'VWAP Short'
    }

    data = [set1, set2, set3, set4]

    layout = go.Layout({
        'title': {
            'text': symbol,
            'font': {
                'size': 25
            }
        }
    })

    fig = go.Figure(data=data, layout=layout).set_subplots(
        2, 1, row_heights=[0.7, 0.3])
    fig.add_trace(go.Scatter(
        x=df[0], y=rsi), row=2, col=1)
    fig.update_layout(height=800, title_text=symbol + " " + interval,
                      xaxis_rangeslider_visible='slider' in [])

    return fig
