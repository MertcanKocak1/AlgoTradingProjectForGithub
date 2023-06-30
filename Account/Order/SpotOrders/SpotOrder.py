from Account.Account import Account
from Database.Database import Database
import time
import ClientData
import pandas as pd
from TelegramBot.Telegram import TelegramBot
from Logger.Logger import Logger
from Enums.OrderEnums import OrderEnums
from Enums.AccountEnums import AccountEnums
from Enums.FileEnums import FileEnums
from Enums.LogEnums import LogEnums
import ClientData

class SpotOrder:
    def __init__(self):
        self.acc = Account.getInstance()
        self.database = Database.getInstance()
        self.tb = TelegramBot.getInstance()
        self.class_name = "SpotOrder"

    def create_new_spot_order(self, side, symbol: str = AccountEnums.TRADING_COIN.value):
        df = pd.read_csv(FileEnums.CSV_FILE.value).iloc[-5:]
        if side == "BUY":
            self.create_buy_order(symbol, df)
        elif side == "SELL":
            self.create_sell_order(symbol, df)

    def create_buy_order(self, symbol: str, df):
        balance = self.acc.spot_get_asset_balance()
        coin_price = self.acc.get_last_price()
        quantity = self.acc.floor_precision_fix((balance / coin_price), 5)
        try:
            order = self.acc.client.order_market_buy(
                symbol=symbol,
                quantity=quantity)
            order['price'] = self.acc.get_last_position_price()
            self.acc.set_last_position_price(order['price'])
            log_id = Logger.add_log(self.class_name, "create_buy_order", OrderEnums.SPOT_LONG_ENTRY.value, "SpotBuy",
                                    False)
            Logger.add_log_detail(log_id, df.iloc[-2].to_json().__str__())
            self.tb.send_message_to_user(("Enter Price", str(df.iloc[-2]['Close']), " and time is : ", time.ctime()))
        except Exception as e:
            Logger.add_log_error(self.class_name, "create_buy_order", e.__str__())

    def create_sell_order(self, symbol: str, df):
        quantity = self.acc.spot_get_asset_balance("BTC")
        try:
            order = self.acc.client.order_market_sell(
                symbol=symbol,
                quantity=quantity)
            order['price'] = self.acc.get_last_position_price()
            self.acc.set_last_position_price()
            log_id = Logger.add_log(self.class_name, "create_sell_order", OrderEnums.SPOT_LONG_EXIT.value, "SpotSell",
                                    False)
            Logger.add_log_detail(log_id, df.iloc[-2].to_json().__str__())
            self.tb.send_message_to_user(("Exit Price", str(df.iloc[-2]['Close']), " and time is : ", time.ctime()))
        except Exception as e:
            Logger.add_log_error(self.class_name, "create_sell_order", e.__str__())
