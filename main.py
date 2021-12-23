from Binance import *
from Strategy import Stratgy
import config
from WebSocket import run_web_socket
socket = f'wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m'
b = Binance(config.API_KEY,config.API_SECRET)
#btc_arr = b.historical_last_in_minutes("BTCUSDT","10")
#eth_arr = b.historical_last_in_minutes("ETHUSDT","10")
run_web_socket()
 