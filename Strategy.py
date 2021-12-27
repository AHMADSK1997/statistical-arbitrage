
import time
import numpy
import pandas as pd
from scipy import stats
from Order import Order
import parameters

class Stratgy():
    def __init__(self, usdt_amount, order_amount, btc_amount, eth_amount):
        self.usdt_amount = usdt_amount
        self.order_amount = order_amount
        self.btc_amount = btc_amount
        self.eth_amount = eth_amount
        self.lastorder = None
        self.is_opened_position = False
        self.period = 10
        self.profit = 0
        self.total_profit = 0
        self.btc_amount_befor_order = btc_amount
        self.eth_amount_befor_order = eth_amount

    def bot_trade(self, btc, eth):
        print('bot trade is runing')
        btc_closes = btc[1:][:,1]
        eth_closes = eth[1:][:,1]
        my_trigger = self.getTrigger(btc, eth)
        print("my-trigger {} ".format(my_trigger))
        if(my_trigger == 'Buy BTC and sell ETH'):
            order = Order(my_trigger, btc[1:][:,0][-1:], btc_closes[-1:],
                             eth_closes[-1:], self.btc_amount, self.eth_amount, self.order_amount)
            self.lastorder = order
            self.saveDataBeforEexchage()
            
            order.exchage()
            self.updateData(order.btc_amount, order.eth_amount, btc_closes[-1:], eth_closes[-1:])

        elif(my_trigger == 'Sell BTC and buy ETH'):
            order = Order(my_trigger, btc[1:][:,0][-1:], btc_closes[-1:],
                             eth_closes[-1:], self.btc_amount, self.eth_amount, self.order_amount)
            
            self.lastorder = order
            self.saveDataBeforEexchage()
            
            order.exchage()
            self.updateData(order.btc_amount, order.eth_amount, btc_closes[-1:], eth_closes[-1:])
        #else:
            #print('do nothing')
        self.usdt_amount = self.btc_amount*btc_closes[-1:]+ self.eth_amount*eth_closes[-1:]
        print('usdt {} '.format(self.usdt_amount))
        print('total {} '.format(self.total_profit))
        print("***********************************")


    def getTrigger(self, btc, eth):
        #print("trigger is runing")
        btc_price = btc[1:][:,1]
        eth_price = eth[1:][:,1]
        my_zscore = self.calculateZscore(btc_price, eth_price)
        print("my zscore {} ".format(my_zscore))
        '''
        print("my UPPER_THRESHOLD {} ".format(parameters.UPPER_THRESHOLD))
        print("my LOWER_THRESHOLD {} ".format(parameters.LOWER_THRESHOLD))
        print("my STOP_LOSS {} ".format(parameters.STOP_LOSS))
        print("my TAKE_PROFIT {} ".format(parameters.TAKE_PROFIT))
        print("my TIME_OUT {} ".format(parameters.TIME_OUT))
        '''
        # open position
        if(self.is_opened_position == False):
            print("open position check")
            if(my_zscore>parameters.UPPER_THRESHOLD):
                self.is_opened_position = True
                return 'Buy BTC and sell ETH'
            elif(my_zscore<parameters.LOWER_THRESHOLD):  
                self.is_opened_position = True
                return 'Sell BTC and buy ETH'
            else: 
                return 'do nothing'
        # close position
        elif(self.is_opened_position == True):
            print("Cheaking close position")
            self.getProfit(btc_price[-1:], eth_price[-1:])
            passedTime = ((btc[1:][:,0][-1:] - self.lastorder.time)/60000)
            #print('passed time {}'.format(passedTime))
            if(self.profit < parameters.STOP_LOSS or self.profit > parameters.TAKE_PROFIT or passedTime > parameters.TIME_OUT):
                if(self.lastorder.order == 'Buy BTC and sell ETH'):
                    self.updateClose()
                    return 'Sell BTC and buy ETH'
                else:
                    self.updateClose()
                    return 'Buy BTC and sell ETH'
            else:
                return 'do nothing'
        
        
    def calculateZscore(self, btc_closes,eth_closes):
        #print("calculateZscore is runing")
       # numpy.info(btc_closes)
        rtio = numpy.divide(btc_closes, eth_closes)
        #print("rtio {} ".format(rtio))
        zscore = stats.zscore(rtio)
        #print("zscore {}".format(zscore[-1:]))
        return zscore[-1:]

    def updateData(self, btc_amount, eth_amount, btc_price, eth_price):
            self.btc_amount = btc_amount
            self.eth_amount = eth_amount
    
    def saveDataBeforEexchage(self):
        self.btc_amount_befor_order = self.btc_amount
        self.eth_amount_befor_order = self.eth_amount

    def updateClose(self):
        self.is_opened_position = False
        self.total_profit += self.profit
        #print('total profit is {}'.format(self.total_profit))
        self.profit = 0

    def getProfit(self, btc_price, eth_price):
            profit_if_order = self.btc_amount*btc_price + self.eth_amount*eth_price
            #print('profit_if_order {}'.format(profit_if_order))
            profit_if_not_order =  self.btc_amount_befor_order*btc_price + self.eth_amount_befor_order*eth_price
            #print('profit_if_not_order {}'.format(profit_if_not_order))
            my_profit = profit_if_order - profit_if_not_order
            print('profit is {}'.format(my_profit))
            #print('usdt is {}'.format(usdt))
            self.profit = my_profit
