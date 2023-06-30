RSI_BUY_SIGNAL = {'FunctionName': 'is_this_value_lower_than', 'FunctionParameters': ['RSI', 40]}
RSI_SELL_SIGNAL = {'FunctionName': 'is_this_value_greater_than', 'FunctionParameters': ['RSI', 60]}

STOTASTIC_CROSSOVER = {'FunctionName': 'is_cross_over', 'FunctionParameters': ['STOCHK', 'STOCHD']}
STOTASTIC_VALUE_LOWER = {'FunctionName': 'is_this_value_lower_than', 'FunctionParameters': ['STOCHK', 50]}
STOTASTIC_VALUE_HIGHER = {'FunctionName': 'is_this_value_greater_than', 'FunctionParameters': ['STOCHK', 70]}
STOTASTIC_CROSSUNDER = {'FunctionName': 'is_cross_under', 'FunctionParameters': ['STOCHK', 'STOCHD']}

MACDHIST_TURNEDGREENER = {'FunctionName': 'is_this_value_turned_greener', 'FunctionParameters': ['MACDHIST']}
MACDHIST_TURNEDREDDER = {'FunctionName': 'is_this_value_turned_redder', 'FunctionParameters': ['MACDHIST']}

IS_EMA50_HIGHER_THAN_CLOSE = {'FunctionName': 'is_this_value_greater_than', 'FunctionParameters': ['EMA50', 'Close']}
IS_EMA100_HIGHER_THAN_CLOSE = {'FunctionName': 'is_this_value_greater_than', 'FunctionParameters': ['EMA100', 'Close']}
IS_EMA200_HIGHER_THAN_CLOSE = {'FunctionName': 'is_this_value_greater_than', 'FunctionParameters': ['EMA200', 'Close']}

IS_EMA50_LOWER_THAN_CLOSE = {'FunctionName': 'is_this_value_lower_than', 'FunctionParameters': ['EMA50', 'Close']}
IS_EMA100_LOWER_THAN_CLOSE = {'FunctionName': 'is_this_value_lower_than', 'FunctionParameters': ['EMA100', 'Close']}
IS_EMA200_LOWER_THAN_CLOSE = {'FunctionName': 'is_this_value_lower_than', 'FunctionParameters': ['EMA200', 'Close']}

SAR_CROSS_OVER = {'FunctionName': 'is_cross_over', 'FunctionParameters': ['SAR', 'Close']}
SAR_CROSS_UNDER = {'FunctionName': 'is_cross_under', 'FunctionParameters': ['SAR', 'Close']}
