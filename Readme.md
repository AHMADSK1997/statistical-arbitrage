# Statistical Arbitrage


## About The Project
In this project, we implemented the statistical arbitrage strategy with a machine learning algorithm called [genetic algorithm](https://pygad.readthedocs.io/en/latest/), in brief we collected the historical data from Binance website of BTC and Ethereum for the past two years, the difference between each data point was a minute, which was 1 million data in total for each currency, the data was used for the genetic algorithm which trained on it, learnt it and created parameters that the statistical arbitrage require to do the mathematics to know when to buy a currency and sell the other simultaneously
The user of the application will have to choose how much money he wants to use for the trades, and how much percent of it is he willing to invest in each trade
after that the user can choose to start with the current parameters or optimize them for higher and better profit which might be a little slower though
Our project is a web page built using Python, html, CSS, and [flask](https://flask.palletsprojects.com/en/2.0.x/) web framework which provides useful tools and features that make creating web applications in Python easier. It also gives flexibility and it’s a very accessible framework for developers since to build a web application quickly using only a single Python file.


## Statistical arbitrage
Statistical arbitrage is supposedly one of the most popular types of trading strategy. In this strategy, usually a pair of stocks are traded in a market-neutral strategy, it doesn’t matter whether the market is trending upwards or downwards, the two open positions for each stock hedge against each other.
Historically, Statistical arbitrage evolved out of the simpler pairs trade strategy, in which stocks are put into pairs by fundamental or market-based similarities. When one stock in a pair outperforms the other, the underperforming stock is bought long, and the outperforming stock is sold short with the expectation that under performing stock will climb towards its outperforming partner. Mathematically speaking, the strategy is to find a pair of stocks with high correlation, cointegration, or other common factor characteristics.
![alt text](https://imgur.com/qJmJ1q5.png)

## Parameters 
### The z-score
Simply put, given a normal distribution of raw data points z-score is calculated so that the new distribution is a normal distribution with mean 0 and standard deviation of 1. Having such a distribution ~ N(0, 1) is very useful for creating threshold levels. For example, in pairs trading, we have a distribution of spread between the prices of stocks A and B. We can convert these raw scores of spread into z-scores as explained below. This new distribution will have mean 0 and standard deviation of 1.
To calculating z-score we use the formula:
z = (x – mean) / standard deviation, where x is a raw data point and z is the z-score.
Mean and standard deviation can be rolling statistics for a period of ‘t’ days or minutes or time intervals.
Using these concepts of moving averages and z-score we create the entry points for Pairs Trading.

* Entry point 
    1. Upper Threshold
    2. Lower Threshold
    ![alt text](https://imgur.com/am0gG5F.png)
* Exit point
    1.	STOP LOSS
    2.	TAKE PROFIT
    3.	TIME OUT
    ![alt text](https://imgur.com/fLaZQbz.png)


## Run the code

It works on [Python 3.9.0 ](https://www.python.org/downloads/release/python-390/)
  ```
  git clone https://github.com/AHMADSK1997/statistical-arbitrage.git
  pip install -r requirements.txt
  python app.py
  ```
  Connect to http://localhost:5000
### Home page
![alt text](https://imgur.com/x9QO2vz.png)
This is the home page of the project, you can enter the amount of money you want to invest, and how much percent you want to invest in each trade, then you can start, below that there’s a table that describes the history of events, a new row is added every minute,  the first column displays the date, the second is the amount of bitcoin currencies and the third is the amount of Ethereum currencies, the fourth column is the history of portfolio (the sum of the BTC and ETH in USD) then comes the history of events (whether it was buy BTC and sell ETH or vice versa) and then two columns for the exact prices in USD of the currencies at the time of the trade, you can also download the history of events as an excel file by clicking on Download CSV.

### Genetic Algorithm page
![alt text](https://imgur.com/Jh42LEm.png)
Here the GA page, the user can see the parameters and can optimize them if he want.
When click on Optimize parameters it will take some time until update them.

### Live data graph 
![alt text](https://imgur.com/CWeCDzA.png)
This graph outlines the real-time price of Bitcoin. The y-axis shows the fluctuation of price in Bitcoin in USDT, the x-axis illustrates the time-period and allows the user to adjust the specific period being viewed. The y-axis shows the fluctuation of price in Bitcoin. 

### Portfolio
![alt text](https://imgur.com/M81QM08.png)
The Portfolio graph illustrates how the total value of your portfolio for a specific asset class (or a subset of your portfolio) will change, based on a percent change in the price of the cryptocurrencies. Available settings may change based on the asset class displayed.