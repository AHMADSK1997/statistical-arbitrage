import csv
from datetime import datetime
import threading
from flask import Flask, render_template, jsonify, request, redirect, Response
from threading import Lock
from flask.helpers import url_for
from flask_socketio import SocketIO, emit
import pandas as pd
from Binance import Binance
from GeneticAlgorithm import runGa
from Strategy import Stratgy
import parameters
import config
import websocket, json, numpy
from binance.client import Client
from csv import writer
import pandas as pd
import time as t
btc_price = None
eth_price = None
closesBtc = []
closesEth = []
lastorder = None
stratgy = Stratgy(0, 0, 0, 0)
data = {'btc': 0 , 'eth': 0, 'usdt': 0, 'event':' '}
field_names = ['date','btc', 'eth', 'usdt', 'event']
time = t.time()*1000
flag = False
async_mode = None
client = Client(config.API_KEY, config.API_SECRET, tld='us')
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


with open('event.csv', 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(field_names)


def background_thread():
    global data
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(60)
        #now = str(time.day)+'/'+str(time.month)+'/'+str(time.year)+'  ,'+str(time.hour)+':'+'0'+str(time.minute)
        append_list_as_row('event.csv',[time, round(data['btc'],4),round(data['eth'],4) ,round(data['usdt'],4),data['event']])
        socketio.emit('my_response',
                    {'date':  datetime.fromtimestamp(time/1000).strftime("%Y-%m-%d, %H:%M"),
                    'btc': round(data['btc'],4),
                    'eth' : round(data['eth'],4),
                    'usdt': round(data['usdt'],4),
                    'event':data['event']})
        socketio.emit('portfolio',{'time':time,'usdt':round(data['usdt'],4)})

@app.route('/<usdt>/<amount>', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def home():
    table = getDatafromExel('event.csv',0)
    for i in range(len(table[:,0])):
        date =datetime.fromtimestamp(table[:,0][i]/1000).strftime("%Y-%m-%d, %H:%M")
        table[:,0][i] = date
    if(stratgy.order_amount == 0):
        return render_template('index.html',table=table)
    else:
        return render_template('index.html',table=table, usdt=stratgy.usdt_start, amount=stratgy.order_amount*100/stratgy.usdt_start)

@app.route('/BTCUSDT', methods=['GET','POST'])
def btc():
    return render_template('btc.html',title='BTCUSDT')


@app.route('/ETHUSDT', methods=['GET','POST'])
def eth():
    return render_template('eth.html',title='ETHUSDT')

@app.route('/ga', methods=['GET','POST'])
def ga():
    return render_template('ga.html',Stoploss=round(parameters.STOP_LOSS,4),
                                        Takeprofit=round(parameters.TAKE_PROFIT,4),
                                        Timeout=round(parameters.TIME_OUT,4),
                                        Upper=round(parameters.UPPER_THRESHOLD,4),
                                        Lower=round(parameters.LOWER_THRESHOLD,4))

@app.route('/portfolio', methods=['GET','POST'])
def portfolio():
    points = portfolio_data()
    return render_template('portfolio.html',points=points)

@app.route("/forward/", methods=['POST'])
def my_link():
    params = runGa()
    return render_template('ga.html', Stoploss=round(params[0],4),
                                        Takeprofit=round(params[1],4),
                                        Timeout=round(params[2],4),
                                        Upper=round(params[3],4),
                                        Lower=round(params[4],4))

@app.route("/start/", methods=['POST'])
def start():
    global thread
    usdt = float(request.form.get('usdt'))
    percentage_amount = float(request.form.get('quantity'))
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    run_web_socket_thread(usdt, percentage_amount)
    '''
    socketio.emit('my_response',
                        {'date': datetime.fromtimestamp(time/1000).strftime("%Y-%m-%d, %H:%M"),
                        'btc': round(data['btc'],4),
                        'eth' : round(data['eth'],4),
                        'usdt': round(data['usdt'],4),
                         'event':data['event']})
    '''
    return redirect(url_for('home'))

'''
@socketio.event
def connect():
    #append_list_as_row('event.csv',[round(data['btc'],4),round(data['eth'],4) ,round(data['usdt'],4),data['event']])
    emit('my_response', {'date': datetime.fromtimestamp(time/1000).strftime("%Y-%m-%d, %H:%M"),
                        'btc': round(data['btc'],4),
                        'eth' : round(data['eth'],4),
                        'usdt': round(data['usdt'],4),
                        'event': data['event']})
'''
@app.route('/history/<stock>',methods=['GET','POST'])
def history(stock):
    candlesticks = client.get_historical_klines(stock, Client.KLINE_INTERVAL_15MINUTE, "15 day ago UTC")
    processed_candlesticks = []
    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }

        processed_candlesticks.append(candlestick)
    return jsonify(processed_candlesticks)


@app.route('/portfolio_data',methods=['GET','POST'])
def portfolio_data():
    table = getDatafromExel('event.csv',0)
    list_usdt = []
    if(len(table[:,3])==0):
        return (list_usdt)
    for i in range(len(table[:,3])):
        list_usdt.append([table[:,0][i], table[:,3][i]])
    return (list_usdt)

@app.route("/DownloadCsv")
def DownloadCsv():
    table = getDatafromExel('event.csv',0)
    csv = 'Date,BTC,ETH,Portfolio,event\n'
    for line in table:
        for i in range(len(line)):
            if i==0 :
                date =datetime.fromtimestamp(line[i]/1000).strftime("%Y-%m-%d  %H:%M")
                csv += date
            else:
                csv = csv + ',' + str(line[i])
        csv += '\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=results.csv"})

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global btc_price, eth_price, closesBtc, closesEth, stratgy, flag, data, time
    json_message = json.loads(message)
    data_json = json_message['data']
    candle = data_json['k']
    symbol = candle['s']
    is_candle_closed = candle['x']
    close = candle['c']
    time = candle['t']
    if is_candle_closed:
    # start if
        #print("candle closed at {}".format(close))
        if(symbol=='BTCUSDT'):
            btc_price = float(close)
        if(symbol=='ETHUSDT'):
            eth_price = float(close)
        if(btc_price != None and eth_price != None):
            closesBtc = numpy.append(closesBtc, [[time,btc_price]], axis=0)
            closesEth = numpy.append(closesEth, [[time,eth_price]], axis=0) 
            #print("***********************************")
            #print("call to the trade strategy") # create the trade strategy
            data = stratgy.bot_trade('pairs trading', closesBtc, closesEth)
            btc_price = None
            eth_price = None
           
    # end if


def run_web_socket_thread(usdt, percentage_amount):
    init(usdt, percentage_amount)
    socket = f'wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m'
    ws = websocket.WebSocketApp(socket, on_open=on_open ,on_message=on_message, on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()



def init(start_usdt, percentage_amount):
    global stratgy, closesBtc , closesEth
    b = Binance(config.API_KEY,config.API_SECRET)
    closesBtc = b.historical_last_in_minutes("BTCUSDT","10")
    closesEth = b.historical_last_in_minutes("ETHUSDT","10")
    order_amount = start_usdt * percentage_amount / 100
    data['btc'] = (start_usdt/2)/float(closesBtc[1:][:,1][-1:])
    data['eth'] = (start_usdt/2)/float(closesEth[1:][:,1][-1:])
    data['usdt'] = start_usdt
    socketio.emit('my_response', {'date': datetime.fromtimestamp(time/1000).strftime("%Y-%m-%d, %H:%M"),
                                'btc': data['btc'],
                                'eth' : data['eth'],
                                'usdt': data['usdt']})
    append_list_as_row('event.csv',[int(int(time/10000)*10000), round(data['btc'],4),round(data['eth'],4) ,round(data['usdt'],4),data['event']])
    stratgy = Stratgy(start_usdt, order_amount, data['btc'], data['eth'])

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def getDatafromExel(file_name, start):
    try:
        df = pd.read_csv(file_name, skiprows=start)
        df.columns = ['date','btc','eth','usdt','event']
        df.to_dict('records')
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    return df.to_numpy()
    
if __name__ == "__main__":
    socketio.run(app)