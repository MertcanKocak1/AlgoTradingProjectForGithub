from binance.enums import *

import ClientData
from Account.Account import Account
from Database.Database import Database
from Logger.Logger import Logger

from Enums.OrderEnums import OrderEnums
from Enums.AccountEnums import AccountEnums

class ShortOrderExit:
    def __init__(self):
        self.acc = Account.getInstance()
        self.database = Database.getInstance()
        self.class_name = "ShortOrderExit"

    def Execute(self):
        try:
            order = self.acc.client.create_margin_order(symbol=AccountEnums.TRADING_COIN.value
                                                        , side=SIDE_BUY
                                                        , isIsolated='TRUE'
                                                        , type=ORDER_TYPE_MARKET
                                                        , sideEffectType="MARGIN_BUY"
                                                        , quantity=self.get_total_btc_to_close_position())
            order['price'] = self.acc.calculate_weighted_avg(order)
            order['side'] = "SHORTEXIT"
            order['commission'] = self.acc.sum_of_commission(order)
            ClientData.marginLastPosition = 0
            self.repay_upper_coin_loan()
            log_id = Logger.add_log(self.class_name, "Execute", OrderEnums.MARGIN_LONG_EXIT.value, "MarginLongExit",
                                    False)
            Logger.add_log_detail(log_id, order)
        except Exception as e:
            Logger.add_log_error(self.class_name, "Execute", e.__str__())

    def repay_upper_coin_loan(self):
        try:
            borrowed_amount = self.acc.floor_precision_fix(
                float(self.acc.client.get_isolated_margin_account()['assets'][0]['baseAsset']['borrowed']), 5)
            response = self.acc.client.repay_margin_loan(asset=AccountEnums.TRADING_COIN_UPPER
                                                         , amount=borrowed_amount
                                                         , symbol=AccountEnums.TRADING_COIN.value
                                                         , isIsolated='TRUE')
            log_id = Logger.add_log(self.class_name, "repay_upper_coin_loan", "Margin_repay_btc", "MarginRepayBtc",
                                    False)
            Logger.add_log_detail(log_id, response)
        except Exception as e:
            Logger.add_log_error(self.class_name, "repay_upper_coin_loan", e.__str__())

    def get_total_btc_to_close_position(self):
        # I don't know how to do dynamic get total btc to close position because of netAssetOfBtc
        return self.acc.floor_precision_fix(float(
            self.acc.client.get_isolated_margin_account()['assets'][0]['quoteAsset']['netAssetOfBtc']) / 100 * 99.5, 5)
