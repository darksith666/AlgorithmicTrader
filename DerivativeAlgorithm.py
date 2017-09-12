import numpy as np
import pandas as pd
from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage

def initialize(context):  
    schedule_function(open_positions, date_rules.every_day(), time_rules.market_close())
    context.stock=sid(351)
    pipe = Pipeline()
    attach_pipeline(pipe, 'pipeline')
    pipe.add(slope, 'slope')
    pipe.set_screen(slope>0)
    context.stocks_sold = []
    
def before_trading_start(context, data):
    output = pipeline_output('pipeline')
    context.my_universe = output.sort_values('slope', ascending=False).iloc[:25]
    context.assets=(context.my_universe.index)    
    
def open_positions(context,data):
    slopePeaktoPeak=calculateSlope(context,data)
    printSlope=str(slopePeaktoPeak)
    printStock=str(context.stock)
    print("The Trend slope of " + printStock +" is " + printSlope)
    if(slopePeaktoPeak>0 and data.can_trade):
        order_target_percent(context.stock, 1.00)
    if(slopePeaktoPeak<=0 and data.can_trade):
        order_target_percent(context.stock, 0.00)
    record('Leverage',context.account.leverage)

def calculateSlope(context,data):
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
    slopePeaktoPeak=slopePeaktoPeak/highestValue
    return slopePeaktoPeak
        
    

            
        
        
        

           