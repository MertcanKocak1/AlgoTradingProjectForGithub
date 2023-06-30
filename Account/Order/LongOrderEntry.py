from binance.enums import *

import ClientData
from Account.Account import Account
from Database.Database import Database
from Logger.Logger import Logger
from Enums.OrderEnums import OrderEnums
from Enums.AccountEnums import AccountEnums


class LongOrderEntry:
    def __init__(self):
        self.acc = Account.getInstance()
        self.database = Database.getInstance()
        self.class_name = "LongOrderEntry"

    def Execute(self):
        try:
            self.loan_lower_coin()
            lastFree = self.acc.client.get_isolated_margin_account()['assets'][0]['quoteAsset']['free']
            order = self.acc.client.create_margin_order(symbol=AccountEnums.TRADING_COIN.value
                                                        , side=SIDE_BUY
                                                        , isIsolated='TRUE'
                                                        , type=ORDER_TYPE_MARKET
                                                        , quantity=self.total_upper_coin_to_buy(lastFree))
            order['price'] = self.acc.calculate_weighted_avg(order)
            order['side'] = "LONGENTRY"
            order['commission'] = self.acc.sum_of_commission(order)
            log_id = Logger.add_log(self.class_name, "Execute", OrderEnums.MARGIN_LONG_ENTRY.value, "MarginLongEntry",
                                    False)
            Logger.add_log_detail(log_id, order)
            ClientData.marginLastPosition = order['price']
        except Exception as e:
            Logger.add_log_error(self.class_name, "Execute", e.__str__())

    def total_upper_coin_to_buy(self, total) -> float:
        try:
            btcPrice = self.acc.floor_precision_fix(float(self.acc.client.get_margin_price_index(
                symbol=AccountEnums.TRADING_COIN.value)['price']), 5)
            return self.acc.floor_precision_fix(((float(total) / btcPrice) / 100 * 99), 5)
        except Exception as e:
            Logger.add_log_error(self.class_name, "total_upper_coin_to_buy", e.__str__())

    def loan_lower_coin(self):
        try:
            maxAmount = self.acc.floor_precision_fix(
                self.acc.get_max_margin_amount(AccountEnums.TRADING_COIN_LOWER.value) / 100 * 98, 3)
            response = self.acc.client.create_margin_loan(asset=AccountEnums.TRADING_COIN_LOWER.value
                                                          , amount=maxAmount
                                                          , symbol=AccountEnums.TRADING_COIN.value
                                                          , isIsolated='TRUE')
            log_id = Logger.add_log(self.class_name, "loan_lower_coin", "Margin_repay_usdt", "MarginLoanUsdt",
                                    False)
            Logger.add_log_detail(log_id, response)
        except Exception as e:
            Logger.add_log_error(self.class_name, "loan_lower_coin", e.__str__())
