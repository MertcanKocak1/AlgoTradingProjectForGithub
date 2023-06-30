from binance.enums import *

import ClientData
from Account.Account import Account
from Database.Database import Database
from Logger.Logger import Logger
from Enums.OrderEnums import OrderEnums
from Enums.AccountEnums import AccountEnums

class LongOrderExit:
    def __init__(self):
        self.acc = Account.getInstance()
        self.database = Database.getInstance()
        self.class_name = "LongOrderExit"

    def Execute(self):
        try:
            order = self.acc.client.create_margin_order(symbol=AccountEnums.TRADING_COIN_SYMBOL,
                                                        side=SIDE_SELL,
                                                        isIsolated='TRUE',
                                                        type=ORDER_TYPE_MARKET,
                                                        quantity=self.get_total_upper_coin())
            self.repay_lower_coin()
            order['price'] = self.acc.calculate_weighted_avg(order)
            order['side'] = "LONGEXIT"
            order['commission'] = self.acc.sum_of_commission(order)
            ClientData.marginLastPosition = 0
            log_id = Logger.add_log(self.class_name, "Execute", OrderEnums.MARGIN_LONG_EXIT.value, "MarginLongExit",
                                    False)
            Logger.add_log_detail(log_id, order)
        except Exception as e:
            Logger.add_log_error(self.class_name, "Execute", e.__str__())

    def repay_lower_coin(self):
        borrowed = self.acc.client.get_isolated_margin_account()['assets'][0]['quoteAsset']['borrowed']
        try:
            response = self.acc.client.repay_margin_loan(asset=AccountEnums.TRADING_COIN_LOWER.value
                                                         , amount=borrowed
                                                         , symbol=AccountEnums.TRADING_COIN.value
                                                         , isIsolated='TRUE')
            log_id = Logger.add_log(self.class_name, "repay_lower_coin", "Margin_repay_usdt", "MarginRepayUsdt",
                                    False)
            Logger.add_log_detail(log_id, response)
        except Exception as e:
            Logger.add_log_error(self.class_name, "repay_lower_coin", e.__str__())

    def get_total_upper_coin(self) -> float:
        try:
            return self.acc.floor_precision_fix(
                float(self.acc.client.get_isolated_margin_account()['assets'][0]['baseAsset']['netAsset']), 5)
        except Exception as e:
            Logger.add_log_error(self.class_name, "get_total_upper_coin", e.__str__())
