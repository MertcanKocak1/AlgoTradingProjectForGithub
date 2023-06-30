import inspect
import ClientData

oneRowNeededFunctions = ['is_this_value_greater_than', 'is_this_value_lower_than']
twoRowNeededFunctions = ['is_cross_over', 'is_cross_under', 'is_this_value_greater_than_previous',
                         'is_this_value_lower_than_previous']
threeRowNeededFunctions = []
functionsAndRowCounts = {1: oneRowNeededFunctions, 2: twoRowNeededFunctions, 3: threeRowNeededFunctions}
row_count = 'RowCount'
one_row = 'OneRow'
two_row = 'TwoRow'
three_row = 'ThreeRow'


# Strategy functions    -----------------------------------
def add_property(name, value):
    def decarator(func):
        setattr(func, name, value)
        return func

    return decarator


def find_decorated_functions(decorator):
    decorated_functions = []
    for name, obj in inspect.getmembers(inspect.getmodule(decorator)):
        if inspect.isfunction(obj):
            if hasattr(obj, row_count):
                decorated_functions.append(obj)
    return decorated_functions


def getRowCount(functionName):
    try:
        return next((key for key, value in functionsAndRowCounts.items() if functionName in value))
    except StopIteration:
        return None


def find_func_decorated_row_count(func):
    return getattr(func, row_count)


@add_property(row_count, one_row)
def is_this_value_greater_than(row, colName, value) -> bool:
    if type(value) == int:
        return row.iloc[-1][colName] > value
    elif type(value) == str:
        return row.iloc[-1][colName] > row.iloc[-1][value]


@add_property(row_count, one_row)
def is_this_value_lower_than(row, colName, value) -> bool:
    if type(value) == int:
        return row.iloc[-1][colName] < value
    elif type(value) == str:
        return row.iloc[-1][colName] < row.iloc[-1][value]


@add_property(row_count, two_row)
def is_cross_over(rows, col1, col2) -> bool:
    if len(rows) == 2:
        return rows.iloc[-1][col1] < rows.iloc[-1][col2] and rows.iloc[-2][col1] > rows.iloc[-2][col2]


@add_property(row_count, two_row)
def is_cross_under(rows, col1, col2) -> bool:
    if len(rows) == 2:
        return rows.iloc[-1][col1] > rows.iloc[-1][col2] and rows.iloc[-2][col1] < rows.iloc[-2][col2]


@add_property(row_count, two_row)
def is_this_value_greater_than_previous(rows, col1, col2) -> bool:
    if len(rows) == 2:
        return rows.iloc[-1][col1] > rows.iloc[-2][col2]


@add_property(row_count, two_row)
def is_this_value_lower_than_previous(rows, col1, col2) -> bool:
    if len(rows) == 2:
        return rows.iloc[-1][col1] < rows.iloc[-2][col2]


@add_property(row_count, three_row)
def is_this_value_turned_greener(rows, colName):
    if len(rows) == 3:
        return rows.iloc[-1][colName] >= 0 and rows.iloc[-3][colName] > rows.iloc[-2][colName] \
            and rows.iloc[-2][colName] < rows.iloc[-1][colName]


@add_property(row_count, three_row)
def is_this_value_turned_redder(rows, colName):
    if len(rows) == 3:
        return rows.iloc[-1][colName] <= 0 and rows.iloc[-3][colName] < rows.iloc[-2][colName] \
            and rows.iloc[-2][colName] > rows.iloc[-1][colName]


def check_for_take_profit(row, takeProfit) -> bool:
    return row.iloc[-1]['Close'] > ClientData.last_position_price + (
            (ClientData.last_position_price / 100) * takeProfit)


def check_for_stop_loss(row, stopLoss) -> bool:
    return row.iloc[-1]['Close'] < ClientData.last_position_price - ((ClientData.last_position_price / 100) * stopLoss)

