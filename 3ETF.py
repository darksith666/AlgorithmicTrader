import numpy as np
import pandas as pd
#@.0.00: around -20- -26 whole time -.04A -1.05B -.66S -32.7
#@.022:
#@ .045




#I have one very similar to this guy that managed to perform very well ... in the wrong direction. It had about -4% per day. Very consistently lost money. Anyways, when designing your algorithms you should keep in mind that if you have less than 25k in your account that you cannot perform day trades (well 3 per week). This has a HORRIBLE run time if implemented so that the context.stock is an array full of values, rather than just one. Takes like an hour per day of trading on my other one. Never quite got around to fixing it since I was a little busy.









def initialize(context):  
  #  schedule_function(open_positions, date_rules.every_day(), time_rules.market_open())
  
    context.stock=[sid(351)]#default
    context.stockList=[sid(8554)]
    context.boughtStock=[]
def calcSlope(context,data):
    highestValue=0
    secondValue=0
    indexHigh=0
    indexSecond=0
    currentPrice= data.current(context.stock, 'price')
    priceAverage = data.history(context.stock,'price',2,'1d').mean()
    priceList=data.history(context.stock,'price',30,'1d')
    pandaList=pd.Series(data.history(context.stock,'price',30,'1d'))
    slopeList=pd.Series([])
    for index in range(len(pandaList)):
       if(index<29):
        slopeList[index]=pandaList[index+1]-pandaList[index]
    flagToAllowComparison=0
    flagstart=0
    peakList=pd.Series([])
    for index in range(len(slopeList)):
        if(slopeList[index]>0):
            flagstart=1
        if(slopeList[index]<=0 and flagstart==1):
            peakList[index]=pandaList[index+1]
            flagstart=0
        else:
            peakList[index]=0
    
    peakList[29]=currentPrice#The end of a wave can be the maximum point even if the slope does not go from pos to neg. IE it's climbing up at an exponential rate at the end, and the current value is much greater than any other. Since this is a day by day basis, if the current price is the greatest or second greatest price, the slope will be slightly off.
    adjustedPeakList=pd.Series([])
    peakList[0]=pandaList[0]#The begining of wave can also be a peak
    flagLtoR=0
    for index in range(len(peakList)):
        if(index<30):#Requires this or crashes idk why
            if(peakList[index]>highestValue and peakList[index]>secondValue):
                highestValue=peakList[index]
                indexHigh=index
                
            if(peakList[index]<highestValue and peakList[index]>secondValue):
                secondValue=peakList[index]
                indexSecond=index
    slopePeaktoPeak=0
    if(indexHigh-indexSecond==0):#no reason it should fire, but idk its giving me errors
        pass
    else:
        slopePeaktoPeak=((highestValue-secondValue)/(indexHigh-indexSecond))
    if(highestValue==0):
        slopePeaktoPeak= 0
    else:
        slopePeaktoPeak=slopePeaktoPeak/highestValue
    return slopePeaktoPeak
def handle_data(context,data):
    cash=1000
    cost=240
    for stock in context.stockList:
        context.stock=stock
        thisSlope=calcSlope(context,data)
        if(thisSlope>0.022 and data.can_trade and cost<cash and stock not in context.boughtStock):
            cash-=cost
            print("After buy you have: "+str(cash))
            context.boughtStock.append(context.stock)
            order_target_value(context.stock,cost)
        if(thisSlope<=0 and data.can_trade and stock in context.boughtStock):
            cash+=data[stock].price
            context.boughtStock.remove(context.stock)
            print("After sell you have: " +str(cash))
            order_target_value(context.stock, 0.00)
        record('Leverage',context.account.leverage) 
    

