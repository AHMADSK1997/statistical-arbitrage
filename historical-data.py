import config, csv
from binance.client import Client
from datetime import datetime

client = Client(config.API_KEY, config.API_SECRET)

def Read_Save_Data(symbol,interval,startDate,endDate,fileName):
    csvfile = open(fileName, 'w', newline='') 
    candlestick_writer = csv.writer(csvfile, delimiter=',')

    # fetch 1 minute klines for the last day up until now
    candlesticks = client.get_historical_klines(symbol, interval, startDate, endDate)

    for candlestick in  candlesticks:
        #candlestick[0] = candlestick[0] / 1000
        #candlestick[0] = datetime.fromtimestamp(candlestick[0])
        candlestick_writer.writerow([candlestick[0],candlestick[4]]) # time and close
    csvfile.close()

Read_Save_Data("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE,"1 Jan, 2020","23 Dec, 2021", "BTC-1-minute.csv")
Read_Save_Data("ETHUSDT", Client.KLINE_INTERVAL_1MINUTE,"1 Jan, 2020","23 Dec, 2021", "ETH-1-minute.csv")