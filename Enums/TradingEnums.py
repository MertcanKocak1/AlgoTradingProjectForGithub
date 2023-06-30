from enum import Enum


class TradingEnums(str, Enum):
    SHORT = 'SHORT'
    LONG = 'LONG'
    STOP_LOSS = 'STOP_LOSS'
    TAKE_PROFIT = 'TAKE_PROFIT'
    ENTER_POSITION = 'Enter Position'
    EXIT_POSITION = 'Exit Position'
    FUNCTIONS = 'Functions'
    SPOT = 'SPOT'
