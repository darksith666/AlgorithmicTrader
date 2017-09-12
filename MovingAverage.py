from quantopian.algorithm import attach_pipeline, pipeline_output
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.factors import SimpleMovingAverage
#I can't remember if this one was provided by Quantopian or not. Either way I changed a bunch of stuff in here. I think. In the original one I don't think it handles leverage so it shoots the moon. This is a pretty simple implementation of the pipeline if you want to try looking at how it's implemented. It was probably that one thing I never really got well for a while. I didn't have this one running cause I don't remember it being particularly great. Generally followed the market trend. Handles for leverage, however it will not use 100% of ones leverage at once. Running it from 1/05/16 to 3/3/2017 has a -3.51% ret

def initialize(context):
    schedule_function(endOfDaySale, date_rules.every_day(), time_rules.market_close(hours=1))
    schedule_function(startOfDayBuy, date_rules.every_day(), time_rules.market_open(hours=1))
    pipe = Pipeline()
    attach_pipeline(pipe, 'pipeline_tutorial')
    _50ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=50)
    _200ma = SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=200)
    pipe.add(_50ma, '_50ma')
    pipe.add(_200ma, '_200ma')
    pipe.add(_50ma/_200ma, 'ma_ratio')
    delta=_50ma/_200ma
    percentile=delta.percentile_between(80,100)
    pipe.set_screen(_50ma/_200ma > 1.0 and percentile)
    context.stocks_sold = []
def before_trading_start(context, data):
    output = pipeline_output('pipeline_tutorial')
    context.my_universe = output.sort_values('ma_ratio', ascending=False).iloc[:20]
    context.assets=(context.my_universe.index)

def startOfDayBuy(context, data):
    purchaseValue=50
    cash=context.portfolio.cash
    for stock in context.assets:
            if stock not in context.portfolio.positions:
                if purchaseValue < cash:
                    order_target_value(stock,purchaseValue)
                    cash -= purchaseValue
                    if stock in context.stocks_sold:
                                context.stocks_sold.remove(stock)
                    
   # print("Capital Used: "+str(context.portfolio.capital_used))
    #print("Portfolio value: " +str(context.portfolio.positions_value))
    print("Change in Value: " +str(context.portfolio.capital_used+context.portfolio.positions_value))
    print("Porfolio Cash: " +str(context.portfolio.cash))
    record('Leverage',context.account.leverage)

def endOfDaySale(context,data):
     for stock in context.portfolio.positions:
        if stock not in context.my_universe.index and stock not in context.stocks_sold:
            order_target_value(stock, 0)
            #################################
            context.stocks_sold.append(stock)
              