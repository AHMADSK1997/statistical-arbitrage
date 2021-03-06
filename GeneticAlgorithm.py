import numpy as np
from geneticalgorithm import geneticalgorithm as ga
import pandas as pd
import parameters
from Strategy import *

i=0
btc_arr = None
eth_arr = None
def f(X):
    global btc_arr,eth_arr,i
    if(i == 0):
        btc_arr = getDatafromExel(100 ,'BTC-1-minute.csv', 0)
        eth_arr = getDatafromExel(100 ,'ETH-1-minute.csv', 0)
        profit = fitnessHelp(btc_arr, eth_arr, X)
        #print(btc_arr)
        i+=100
    else:
        btc_row = getDatafromExel(1, 'BTC-1-minute.csv', i)
        eth_row = getDatafromExel(1, 'ETH-1-minute.csv', i)
        btc_arr = np.delete(btc_arr, 0, axis=0)
        btc_arr = np.append(btc_arr, btc_row, axis=0)
        eth_arr = np.delete(eth_arr ,0, axis=0)
        eth_arr = np.append(eth_arr, eth_row, axis=0)
        profit = fitnessHelp(btc_arr, eth_arr, X)
        i+=1
    return -profit

def getDatafromExel(num_of_points ,file_name, start):
    df = pd.read_csv(file_name, skiprows=start, nrows=num_of_points)
    df.columns = ['time','price']
    df.to_dict('records')
    return df.to_numpy()
# arr[stoploss,takeprofit,timeout,UPPER_THRESHOLD,LOWER_THRESHOLD]
varbound=np.array([[-1000,1000],[-1000,1000],[0,50],[0,10],[-10,0]])
vartype=np.array([['int'],['int'],['int'],['real'],['real']])

algorithm_param = {'max_num_iteration': 1000,\
                   'population_size':10,\
                   'mutation_probability':0.1,\
                   'elit_ratio': 0.01,\
                   'crossover_probability': 0.5,\
                   'parents_portion': 0.3,\
                   'crossover_type':'uniform',\
                   'max_iteration_without_improv':None}

model=ga(function=f,\
            dimension=5,\
            variable_type='real',\
            variable_boundaries=varbound,\
            variable_type_mixed=vartype,\
            algorithm_parameters=algorithm_param)

def runGa():
    model.run()
    return model.best_variable


def fitnessHelp(btc_arr, eth_arr, prams):
    parameters.STOP_LOSS = prams[0]
    parameters.TAKE_PROFIT = prams[1]
    parameters.TIME_OUT = prams[2]
    parameters.UPPER_THRESHOLD = prams[3]
    parameters.LOWER_THRESHOLD = prams[4]
    start_usdt = 100000
    btc_amount = (start_usdt/2)/(btc_arr[:,1][len(btc_arr)-1])
    etc_amount = (start_usdt/2)/(eth_arr[:,1][len(eth_arr)-1])
    stratgy = Stratgy(100000, 25000, btc_amount, etc_amount)  
    for i in range (len(btc_arr)):
        stratgy.bot_trade('genetic algorithm', btc_arr[i:i+6],eth_arr[i:i+6])
   # print("the prifit ######### {}".format(stratgy.total_profit))
    return stratgy.total_profit

#runGa()

#   [-2.77000000e+02  4.95000000e+02  1.70000000e+01  5.35521024e-02 -1.35114025e+00]
#   [-156.          328.            5.            2.82306724   -0.92496072]
#   [-392.          291.            4.            0.48588477   -1.12912214]
#   [-6.33000000e+02  5.38000000e+02  3.60000000e+01  7.13111702e+00 -4.45071649e-01]

'''
 [-362.          978.           36.            1.51546964   -1.55107457]

 Objective function:
 -1156.812043838232
'''
'''
 [-5.30000000e+02  3.63000000e+02  2.00000000e+01 -9.63696057e-02
  3.57042739e+00]

 Objective function:
 -1595.4420475569787
'''