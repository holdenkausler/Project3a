from flask import Flask, render_template, request, redirect, url_for
import requests
import pygal
import csv
from datetime import datetime

app = Flask(__name__)
api_key = 'L3N6WZF86JZURK2W'

def filter_data_by_date(data, start_date, end_date):
    time_series_data = None
    for key in data.keys():
        if 'Time Series' in key:
            time_series_data = data[key]
            break

    if time_series_data is None:
        return {}
    
    filtered_data = {}
    for date_str, daily_data in time_series_data.items(): 
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S" if ' ' in date_str else "%Y-%m-%d")
        if start_date <= date <= end_date:
            filtered_data[date_str] = daily_data
    return filtered_data

def create_chart(data, chart_type, symbol):
    dates = sorted(data.keys())
    open_prices = [float(data[date]['1. open']) for date in dates]
    high_prices = [float(data[date]['2. high']) for date in dates]
    low_prices = [float(data[date]['3. low']) for date in dates]
    close_prices = [float(data[date]['4. close']) for date in dates]
    
    chart = pygal.Bar(title=f'{symbol} Stock Prices') if chart_type == "1" else pygal.Line(title=f'{symbol} Stock Prices')
    chart.x_labels = dates
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    return chart.render_data_uri()

def get_stock_symbols():
    stock_symbols = []
    with open('stocks.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        stock_symbols = [row['Symbol'] for row in reader]
    return stock_symbols

@app.route('/', methods=['GET', 'POST'])
def index():
    stocks = get_stock_symbols()
    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = request.form['chart_type']
        time_series = request.form['time_series']
        start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d")

        params = {
            'function': time_series,
            'symbol': symbol,
            'apikey': api_key,
            'outputsize': 'full'
        }

        if time_series == 'TIME_SERIES_INTRADAY':
            if 'interval' in request.form:
                params['interval'] = request.form['interval']
            else:
                params['interval'] = '5min' 

        url = 'https://www.alphavantage.co/query'
        response = requests.get(url, params=params)
        data = response.json()

        filtered_data = filter_data_by_date(data, start_date, end_date)
        chart_uri = create_chart(filtered_data, chart_type, symbol)
        
        return render_template('index.html', stocks=stocks, chart_uri=chart_uri, symbol=symbol)

    return render_template('index.html', stocks=stocks)

if __name__ == '__main__':
    app.run(host="0.0.0.0")