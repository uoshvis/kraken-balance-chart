import krakenex
from time import sleep
import plotly.graph_objs as go
import plotly.offline as py

import config


def remove_pair(pair):
    """Remove XBT pair ending.
    :param pair: pair name
    :type pair: str
    :returs: symbol without pair ending

    """
    if pair[0] == 'X':
        pair = pair[:-4]
    else:
        pair = pair[:-3]
    return pair


def main():
    k = krakenex.API(key=config.api_key, secret=config.private_key)
    balance = k.query_private('Balance', data=None)['result']

    # Remove zero values
    balance = {k: v for k, v in balance.items() if float(v) > 0.0}

    # List alt coin symbols
    my_assets = list(balance.keys())
    base_assets = ['ZEUR', 'XXBT']
    alt_coins = list(set(my_assets) - set(base_assets))

    # Create altcoin + XBT pair symbol
    pairs = [p + 'XXBT' if p[0] == 'X' else p + 'XBT' for p in alt_coins]
    print(pairs)

    # Does not retrieve multiple pairs
    # tickers = k.query_public('Ticker', data={'pair': pairs})

    # Get ticker information
    tickers = {}

    for pair in pairs:
        print('Getting ', pair)
        ticker = k.query_public('Ticker', data={'pair': pair})
        last_trade = ticker['result'][pair]['c'][0]
        asset_name = remove_pair(pair)
        tickers[asset_name] = {}
        tickers[asset_name]['last_trade'] = last_trade
        tickers[asset_name]['amount'] = balance[asset_name]
        print('Got ', pair)
        sleep(2)

    # Extract labels and values
    labels = []
    values = []

    for key, value in tickers.items():
        labels.append(key)
        last_trade = float(value['last_trade'])
        amount = float(value['amount'])
        values.append(last_trade * amount)

    # Also add XBT label and value
    labels.append('XXBT')
    values.append(float(balance['XXBT']))

    total_BTC = sum(values)

    # Plot pie chart
    title = 'Estimated value: ' + str(total_BTC) + ' BTC'
    layout = go.Layout(title=title)
    trace = go.Pie(labels=labels, values=values)
    fig = go.Figure(data=[trace], layout=layout)
    py.plot(fig, filename='kraken_balance_chart.html')

    # TODO add fiat values to chart


if __name__ == '__main__':
    main()
