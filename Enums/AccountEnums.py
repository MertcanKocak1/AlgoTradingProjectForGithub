from enum import Enum


class AccountEnums(str, Enum):
    TRADING_COIN_UPPER = "BTC"
    TRADING_COIN_LOWER = "USDT"
    TRADING_COIN = TRADING_COIN_UPPER + TRADING_COIN_LOWER
