from datetime import datetime
from binance.client import Client
from binance.enums import *
import config ,csv
import numpy

class Binance():
    def __init__(self, key: str, secret: str):
        self.client = Client(config.API_KEY, config.API_SECRET)

    def get_client(self):
        return self.client

    def historical_last_in_minutes(self, stock, time):
        klines = self.client.get_historical_klines(stock, Client.KLINE_INTERVAL_1MINUTE, time+" minute ago UTC")
        closees = []
        for i in range(len(klines)):
            closees.append([klines[i][0],float(klines[i][4])])
        np_closes = numpy.array(closees)
        #print(np_closes)
        return np_closes

    def Read_Save_Data(self, symbol, startDate, endDate, fileName):
        csvfile = open(fileName, 'w', newline='') 
        candlestick_writer = csv.writer(csvfile, delimiter=',')
        # fetch 1 minute klines for the last day up until now
        candlesticks = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE , startDate, endDate)
        for candlestick in  candlesticks:
            candlestick[0] = candlestick[0] / 1000
            candlestick[0] = datetime.fromtimestamp(candlestick[0])
            candlestick_writer.writerow([candlestick[0],candlestick[4]]) # time and close
        csvfile.close()
