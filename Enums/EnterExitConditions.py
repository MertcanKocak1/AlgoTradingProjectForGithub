from Enums.TradingEnums import TradingEnums


enterConditions = {
    'Eclipse9': {
        TradingEnums.FUNCTIONS.value: [{'FunctionName': 'is_cross_over', 'FunctionParameters': ['SAR', 'Close']},
                                       {'FunctionName': 'is_this_value_lower_than',
                                        'FunctionParameters': ['EMA50', 'Close']},
                                       {'FunctionName': 'is_this_value_lower_than',
                                        'FunctionParameters': ['STOCHK', 50]}],
        TradingEnums.TAKE_PROFIT.value: 0.3,
        TradingEnums.STOP_LOSS.value: 0.3,
    }}
exitConditions = {
    'Eclipse9': [[{'FunctionName': 'is_cross_under', 'FunctionParameters': ['SAR', 'Close']}]]
}
