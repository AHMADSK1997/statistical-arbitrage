import threading
from flask import Flask, render_template, jsonify, request, redirect
from threading import Lock
from flask.helpers import url_for
from flask_socketio import SocketIO, emit
from Binance import Binance
from GeneticAlgorithm import runGa
from Strategy import Stratgy
import parameters
import config
import websocket, json, numpy
from binance.client import Client

btc_price = None
eth_price = None
closesBtc = []
closesEth = []
lastorder = None
stratgy = Stratgy(0, 0, 0, 0)
data = {'btc': 0 , 'eth': 0, 'usdt': 0}
flag = False
async_mode = None
client = Client(config.API_KEY, config.API_SECRET, tld='us')

app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

def background_thread():
    global data
    """Example of how to send server generated events to clients."""
    while True:
        socketio.sleep(5)
        socketio.emit('my_response',
                      {'btc': round(data['btc'],4), 'eth' : round(data['eth'],4) ,'usdt': round(data['usdt'],4)})

@app.route('/<usdt>/<amount>', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def home(usdt=None ,amount=None ):
    if usdt == None or amount == None:
        return render_template('index.html')
    return render_template('index.html',usdt=usdt, amount=amount)

@app.route('/BTCUSDT', methods=['GET','POST'])
def btc():
    return render_template('btc.html',title='BTCUSDT')


@app.route('/ETHUSDT', methods=['GET','POST'])
def eth():
    return render_template('eth.html',title='ETHUSDT')

@app.route('/ga', methods=['GET','POST'])
def ga():
    return render_template('ga.html',Stoploss=parameters.STOP_LOSS,
                                        Takeprofit=parameters.TAKE_PROFIT,
                                        Timeout=parameters.TIME_OUT,
                                        Upper=parameters.UPPER_THRESHOLD,
                                        Lower=parameters.LOWER_THRESHOLD)

@app.route("/forward/", methods=['POST'])
def my_link():
    params = runGa()
    return render_template('ga.html', Stoploss=params[0],
                                        Takeprofit=params[1],
                                        Timeout=params[2],
                                        Upper=params[3],
                                        Lower=params[4])

@app.route("/start/", methods=['POST'])
def start():
    global thread
    usdt = float(request.form.get('usdt'))
    percentage_amount = float(request.form.get('quantity'))
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    run_web_socket_thread(usdt, percentage_amount)
    return redirect(url_for('home', usdt=usdt , amount=percentage_amount))
    #return render_template("index.html")

@socketio.event
def connect():
    emit('my_response', {'btc': data['btc'], 'eth' : data['eth'] ,'usdt': data['usdt']})

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

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global btc_price, eth_price, closesBtc, closesEth, stratgy, flag, data
    json_message = json.loads(message)
    data_json = json_message['data']
    candle = data_json['k']
    symbol = candle['s']
    is_candle_closed = candle['x']
    close = candle['c']
    time = candle['t']
    #if is_candle_closed:
    # start if
    print("candle closed at {}".format(close))
    if(symbol=='BTCUSDT'):
        btc_price = float(close)
    if(symbol=='ETHUSDT'):
        eth_price = float(close)
    if(btc_price != None and eth_price != None):
        closesBtc = numpy.append(closesBtc, [[time,btc_price]], axis=0)
        closesEth = numpy.append(closesEth, [[time,eth_price]], axis=0) 
        print("***********************************")
        print("call to the trade strategy") # create the trade strategy
        data = stratgy.bot_trade(closesBtc,closesEth)
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
    socketio.emit('my_response', {'btc': data['btc'], 'eth' : data['eth'] ,'usdt': data['usdt']})
    stratgy = Stratgy(start_usdt, order_amount, data['btc'], data['eth'])

if __name__ == "__main__":
    socketio.run(app)