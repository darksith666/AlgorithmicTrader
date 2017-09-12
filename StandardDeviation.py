import pandas as pd

#This is the standard deviation algorithm. It works by checking the prices over
#a period of time, determines the standard deviation and buys/sells based on it.
#It also can use my "slopecalculation" algorithm. A sort of derivative of the line
#calculator.I find that making it simple is better. Implementing the slope calculator
#usually makes programs run slow since I'm stupid and had it in the update every
#min area.Feel free to mess around with this one as you will. Does not use any 
#pipeline, but rather one particular stock. I have it papertrading atm with 
#amd and has generated 8.72% over 2 months. 


def initialize(context):
    context.stock=sid(351)
    context.trading_day_counter=0
    context.order_submitted = False
    # Reference to AAPL
    schedule_function(open_positions, date_rules.every_day(), time_rules.market_close())#Sets frequency for how often we want to check the market and when to check it. Right now it's at end cause data I have for checking is end of day. Once done, this will be moved to start of day.
    
    #schedule_function(close_positions, date_rules.every_day(), time_rules.market_close())
    slope=0
    
        
def open_positions(context,data):
    slope=slopeCalculation(context, data)############
   # wrong=0#Handles graph
    #right=0
    histPriceAverage = data.history(context.stock,'price',31,'1d')[:-1].mean()#Take 6 prior days, take out the most recent day then average it
    histVolumeFull=data.history(context.stock,'volume',31,'1d')[:-1]
    histVolumeAverage = data.history(context.stock,'volume',31,'1d')[:-1].mean()#Average of the prior 30 days volume on a given day
    currentVolume = data.history(context.stock,'volume',1,'1d').mean()#For some reason doing data.current doesn't work here for volume. This does the average volume on the particular day only, hence it's just volume on that particular day. Values generated from this do not equal NASDAQ,but is close. Appears to have it's own data pipeline.
    currentPrice= data.current(context.stock, 'price')#Gets the price on given day
    printablePrice=str(currentPrice)#Converts int to str so can be printed
    standardDeviation=histVolumeFull.std()#gets the standard deviation
    TwoDeviationsAway= histVolumeAverage+2*standardDeviation
    direction=0#Used to determine a short or long
    if(context.portfolio.positions[context.stock].last_sale_price>histPriceAverage):
        direction=1
    else:
        direction=-1
    if(currentVolume>TwoDeviationsAway and direction ==1 and slope>0 ):
        print("The current volume is greater than two standard deviations from the mean AND Price going UP, Price is currently " +printablePrice)
        order_target_percent(context.stock, 1.00)
        for security in context.portfolio.positions:#Prints off security name/info
            printP=str(context.portfolio.positions[security].last_sale_price)
            printN=str(security)
            print("The Stock " + printN +" is selling at: " + printP)
            printCH=str(context.portfolio.positions[security].amount)
            printT=str(context.portfolio.portfolio_value)
            print("You own " + printCH +" of " + printN + " for a total investment of " + printT)
    if(currentVolume>TwoDeviationsAway and direction == -1 and slope<0):
        print("The current volume is greater than two standard deviations from the mean AND Price going DOWN, Price is currently " +printablePrice)
        order_target_percent(context.stock, -1.00)
        for security in context.portfolio.positions:
            printP=str(context.portfolio.positions[security].last_sale_price)
            printN=str(security)
            print("The Stock " + printN +" is selling at: " + printP)
            printCH=str(context.portfolio.positions[security].amount)
            printT=str(context.portfolio.portfolio_value)
            print("You own " + printCH +" of " + printN + " for a total investment of " + printT)
            

    
def close_positions(context,data): #Ran at end of day
    context.trading_day_counter +=1
    if (context.trading_day_coounter == 2):
        for security in context.portfolio.positions:
            order_target_percent(security, 0.00)
            context.trading_day_counter=0
     
    
       
        

#Really shitty sell algorithm. If I ever do a look at history while updated every min
#it's shit. I haven't touched this guy in a while, but checking the price every
#min is very ineffecient. Something every 30 min or so sounds better.

#Something along lines every min call the function below and increase a variable
#until it is 30, then check the prices. 
def handle_data(context, data):
   for security in context.portfolio.positions:
      histPriceAverage = data.history(security,'price',31,'1d')[:-1].mean()
      if(context.portfolio.positions[security].last_sale_price>histPriceAverage):
        direction=1
      else:
        direction=-1
      if(context.portfolio.positions[security].last_sale_price >1.1*context.portfolio.positions[security].cost_basis and direction ==1):
            printN=str(context.portfolio.positions[security].sid) 
            printS=str(context.portfolio.positions[security].last_sale_price)
            print("You have now sold Long GOOD " + printN + " at " + printS )
            order_target_percent(security, 0.00)
      if(context.portfolio.positions[security].last_sale_price <0.985*context.portfolio.positions[security].cost_basis and direction ==1):
            printN=str(context.portfolio.positions[security].sid) 
            printS=str(context.portfolio.positions[security].last_sale_price)
            print("You have now sold Long BAD " + printN + " at " + printS )
            order_target_percent(security, 0.00)
      if(context.portfolio.positions[security].last_sale_price <0.9*context.portfolio.positions[security].cost_basis and direction ==-1):
            printN=str(context.portfolio.positions[security].sid) 
            printS=str(context.portfolio.positions[security].last_sale_price)
            print("You have now sold SHORT GOOD " + printN + " at " + printS )
            order_target_percent(security, 0.00)     
      if(context.portfolio.positions[security].last_sale_price >1.015*context.portfolio.positions[security].cost_basis and direction ==-1):
            printN=str(context.portfolio.positions[security].sid) 
            printS=str(context.portfolio.positions[security].last_sale_price)
            print("You have now sold SHORT BAD " + printN + " at " + printS )
            order_target_percent(security, 0.00)
   record('Leverage',context.account.leverage)     
    
           
           