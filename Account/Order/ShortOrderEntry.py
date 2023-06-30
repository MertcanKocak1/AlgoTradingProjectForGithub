from binance.enums import *

import ClientData
from Account.Account import Account
from Account.Order.Order import Order
from Database.Database import Database
from Logger.Logger import Logger
from Enums.OrderEnums import OrderEnums
from Enums.AccountEnums import AccountEnums

class ShortOrderEntry(Order):
    def __init__(self):
        self.acc = Account.getInstance()
        self.database = Database.getInstance()
        self.class_name = "ShortOrderEntry"

    def Execute(self):
        try:
            order = self.acc.client.create_margin_order(symbol=AccountEnums.TRADING_COIN.value
                                                        , side=SIDE_SELL
                                                        , type="MARKET"
                                                        , quantity=self.max_upper_coin_amount()
                                                        , sideEffectType="MARGIN_BUY"
                                                        , isIsolated=True)
            order['price'] = self.acc.calculate_weighted_avg(order)
            order['side'] = "SHORTENTRY"
            order['commission'] = self.acc.sum_of_commission(order)
            log_id = Logger.add_log(self.class_name, "Execute", OrderEnums.MARGIN_SHORT_ENTRY.value, "MarginShortEntry",
                                    False)
            Logger.add_log_detail(log_id, order)
            ClientData.marginLastPosition = order['price']
        except Exception as e:
            Logger.add_log_error(self.class_name, "Execute", e.__str__())

    def max_upper_coin_amount(self):
        try:
            return self.acc.floor_precision_fix(self.acc.get_max_margin_amount(AccountEnums.TRADING_COIN_UPPER.value) / 100 * 99, 5)
        except Exception as e:
            Logger.add_log_error(self.class_name, "max_upper_coin_amount", e.__str__())
