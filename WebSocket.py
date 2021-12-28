import threading
import websocket, json, pprint, numpy
from Binance import Binance
from Strategy import *  
import config
btc_price = None
eth_price = None
closesBtc = []
closesEth = []
lastorder = None
stratgy = Stratgy(0, 0, 0, 0)
flag = False
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global btc_price, eth_price, closesBtc, closesEth, stratgy, flag

    '''
    if flag == False:
            b = Binance(config.API_KEY,config.API_SECRET)
            closesBtc = b.historical_last_in_minutes("BTCUSDT","10")
            closesEth = b.historical_last_in_minutes("ETHUSDT","10")
            start_usdt = 100000
            btc_amount = (start_usdt/2)/float(closesBtc[len(closesBtc)-1]['price'])
            etc_amount = (start_usdt/2)/float(closesEth[len(closesEth)-1]['price'])
            stratgy = Stratgy(start_usdt, 25000, btc_amount, etc_amount)
            flag = True
    '''

    json_message = json.loads(message)
    data = json_message['data']
    candle = data['k']
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
    print(btc_price)
    print(eth_price)
    if(btc_price != None and eth_price != None):
        closesBtc = numpy.append(closesBtc, [[time,btc_price]], axis=0)
        closesEth = numpy.append(closesEth, [[time,eth_price]], axis=0) 
        print("***********************************")
        print("call to the trade strategy") # create the trade strategy
        stratgy.bot_trade(closesBtc,closesEth)
        btc_price = None
        eth_price = None
    # end if
def run_web_socket_thread():
    init()
    #global stratgy, closesBtc, closesEth
    #stratgy = stratgy
    #closesBtc = btc
    #closesEth = eth
    socket = f'wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m'
    ws = websocket.WebSocketApp(socket, on_open=on_open ,on_message=on_message, on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

def run_web_socket():
    init()
    socket = f'wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m'
    ws = websocket.WebSocketApp(socket, on_open=on_open ,on_message=on_message, on_close=on_close)
    ws.run_forever()

def init():
    global stratgy, closesBtc , closesEth
    b = Binance(config.API_KEY,config.API_SECRET)
    closesBtc = b.historical_last_in_minutes("BTCUSDT","10")
    closesEth = b.historical_last_in_minutes("ETHUSDT","10")
    start_usdt = 100000
    btc_amount = (start_usdt/2)/float(closesBtc[1:][:,1][-1:])
    etc_amount = (start_usdt/2)/float(closesEth[1:][:,1][-1:])
    stratgy = Stratgy(start_usdt, 25000, btc_amount, etc_amount)


#run_web_socket()
