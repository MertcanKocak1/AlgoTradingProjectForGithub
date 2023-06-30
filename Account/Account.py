import math
from typing import Optional

from binance import Client
from numpy import average

import ClientData
from Enums.AccountEnums import AccountEnums
from ConfigManager import ConfigManager

def calculate_weighted_avg(order: dict):
    price = []
    weights = []
    for fill in order['fills']:
        price.append(float(fill['price']))
        weights.append(float(fill['qty']))
    return round(average(price, weights=weights), 2)


def sum_of_commission(order: dict):
    return sum(float(fill['commission']) for fill in order['fills'])


class Account:
    __instance = None

    def __init__(self):
        if Account.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            config = ConfigManager()
            self.client = Client(config.api_key, config.api_secret)
            Account.__instance = self

    @staticmethod
    def getInstance():
        if Account.__instance is None:
            Account()
        return Account.__instance

    def get_order_status(self, orderId, symbol=AccountEnums.TRADING_COIN.value) -> bool:
        return self.client.get_margin_order(symbol=symbol, orderId=orderId)['isWorking']

    def get_loan(self, assetName: str, amount: float) -> None:
        self.client.create_margin_loan(asset=assetName, amount=amount)

    def repay_loan(self, assetName: str, amount: float) -> None:
        self.client.repay_margin_loan(asset=assetName, amount=amount)

    def get_last_price(self, symbol=AccountEnums.TRADING_COIN.value) -> float:
        return self.floor_precision_fix(float(self.client.get_ticker(symbol=symbol)['lastPrice']), 5)

    def get_max_margin_amount(self, assetName: str) -> float:
        return self.floor_precision_fix(float(
            self.client.get_max_margin_loan(asset=assetName
                                            , isolatedSymbol=AccountEnums.TRADING_COIN.value
                                            , isIsolated=True)[
                'amount']), 5)

    @staticmethod
    def floor_precision_fix(amount, precision: int):
        return math.floor(amount * 10 ** precision) / 10 ** precision

    def is_client_already_in_margin_order(self,
                                          symbol: str = AccountEnums.TRADING_COIN.value) -> bool:
        return not (self.client.get_open_margin_orders(symbol=symbol).__len__() == 0)

    def spot_get_asset_balance(self, symbol: str = AccountEnums.TRADING_COIN_LOWER.value) -> float:
        return self.floor_precision_fix(float(self.client.get_asset_balance(symbol)['free']), 5)

    def get_last_position_price(self, symbol: str = AccountEnums.TRADING_COIN.value) -> float:
        return self.floor_precision_fix(float(self.client.get_my_trades(symbol=symbol)[-1]['price']), 2)

    def get_last_i_position(self, i, symbol: str = AccountEnums.TRADING_COIN.value) -> float:
        return self.client.get_my_trades(symbol=symbol)[-i:]

    def get_last_margin_position_price(self, symbol: str = AccountEnums.TRADING_COIN.value) -> float:
        return self.floor_precision_fix(
            float(self.client.get_margin_trades(symbol=symbol, isIsolated=True)[-1]['price']),
            2)

    def set_last_position_price(self, value: Optional[int] = None):
        if value == 0:
            ClientData.last_position_price = 0
            return
        ClientData.last_position_price = self.get_last_position_price()
