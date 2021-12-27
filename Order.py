
class Order():
    def __init__(self, order, time, btc_price, eth_price, btc_amount, eth_amount, order_amount):
        self.order = order
        self.time = time
        self.btc_price = btc_price
        self.eth_price = eth_price
        self.btc_amount = btc_amount
        self.eth_amount = eth_amount
        self.order_amount = order_amount

    def exchage(self):
        #print("createing order: {}".format(self.order))
        if(self.order == 'Buy BTC and sell ETH'):
            self.eth_amount -= self.order_amount/self.eth_price
            self.btc_amount += self.order_amount/self.btc_price
        elif(self.order == 'Sell BTC and buy ETH'):
            self.btc_amount -= self.order_amount/self.btc_price
            self.eth_amount += self.order_amount/self.eth_price
        #print('My current BTC is: {}'.format(self.btc_amount))
        #print('My current ETH is: {}'.format(self.eth_amount))
        #parameters.PORTFOLIO_AFER_ORDER = parameters.BTC_AMOUNT*btc_price + parameters.ETH_AMOUNT*eth_price