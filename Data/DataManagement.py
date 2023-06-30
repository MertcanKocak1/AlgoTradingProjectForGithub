import csv
import sys
import time
from datetime import datetime
from typing import Tuple, Optional

import pandas as pd
import pandas_ta
import talib
from binance import Client

import ClientData
import PositionStates.PositionContext
from Account.Account import Account
from Logger.Logger import Logger
from Enums.AccountEnums import AccountEnums
from Enums.FileEnums import FileEnums

sys.setrecursionlimit(10 ** 8)


def two_after_comma(data: pd.Series):
    return "{:.2f}".format(data)


def get_current_time_timestamp() -> int:
    return int(datetime.now().timestamp()) * 1000


class DataManagement:
    def __init__(self):
        self.client = Account.getInstance().client
        self.positionContext = PositionStates.PositionContext.PositionContext()
        self.class_name = "DataManagement"

    def get_last_kline(self, symbol: str = AccountEnums.TRADING_COIN.value, timeMinute: int = 1):
        try:
            data = self.client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE,
                                                     f"{timeMinute} Minute Ago GMT+3")[0][0:7]
        except Exception as e:
            return self.get_last_kline()
        return data

    def initilaze_all_data(self):
        try:
            candlesticks = self.client.get_historical_klines(AccountEnums.TRADING_COIN.value
                                                             , Client.KLINE_INTERVAL_1MINUTE,
                                                             "4 Hours Ago GMT+3")
            col_names = ['OpeningTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime']
            with open(FileEnums.CSV_FILE.value, 'w', encoding='UTF8') as f:
                writer = csv.writer(f)
                writer.writerow(col_names)
                for candlestick in candlesticks:
                    writer.writerow(candlestick)
            f = pd.read_csv(FileEnums.CSV_FILE.value, usecols=[0, 1, 2, 3, 4, 5, 6])
            f.to_csv(FileEnums.CSV_FILE.value, index=False)
            Logger.add_log(self.class_name, "initilaze_all_data", "initilaze_all_data", "initilaze_all_data",
                           False)
        except Exception as e:
            Logger.add_log_error(self.class_name, "initilaze_all_data", e.__str__())

    def calculate_rsi(self, f: pd.DataFrame) -> pd.Series:
        try:
            rsi_data = talib.RSI(f['Close'], timeperiod=14)
            result = rsi_data.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_rsi", e.__str__())
            return pd.Series()

    def calculate_sar(self, f: pd.DataFrame) -> pd.Series:
        try:
            sarData = talib.SAR(f['High'], f['Low'])
            result = sarData.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_sar", e.__str__())
            return pd.Series()

    def calculate_macd(self, f: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
        try:
            macd, macdsignal, macdhist = talib.MACD(f['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
            macd = macd.apply(two_after_comma)
            macdsignal = macdsignal.apply(two_after_comma)
            macdhist = macdhist.apply(two_after_comma)
            return macd, macdsignal, macdhist
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_macd", e.__str__())
            return pd.Series(), pd.Series(), pd.Series()

    def calculate_stoch(self, f: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        try:
            k, d = talib.STOCH(f['High'], f['Low'], f['Close'])
            k = k.apply(two_after_comma)
            d = d.apply(two_after_comma)
            return k, d
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_stoch", e.__str__())
            return pd.Series(), pd.Series()

    def calculate_ema(self, f: pd.DataFrame, emaLength: int) -> pd.Series:
        try:
            ema = talib.EMA(f['Close'], timeperiod=emaLength)
            result = ema.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_ema", e.__str__())
            return pd.Series()

    def calculate_smoothing(self, prices: pd.Series, smoothing_type, smoothing_period) -> pd.Series:
        try:
            if smoothing_type == 'sma':
                return talib.SMA(prices, smoothing_period)
            elif smoothing_type == 'ema':
                return talib.EMA(prices, smoothing_period)
            elif smoothing_type == 'rma':
                return pandas_ta.rma(prices, smoothing_period)
            elif smoothing_type is None:
                return prices
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_smoothing", e.__str__())
            return pd.Series()

    def calculate_atr(self, f) -> pd.Series:
        try:
            atr = self.calculate_smoothing(talib.TRANGE(
                f['High'],
                f['Low'],
                f['Close'],
            ), "rma", 14)
            result = atr.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_atr", e.__str__())
            return pd.Series()

    def calculate_bollinger_bands(self, f) -> Tuple[pd.Series, pd.Series, pd.Series]:
        try:
            upper, middle, lower = talib.BBANDS(f['Close'], 20)
            upper = upper.apply(two_after_comma)
            middle = middle.apply(two_after_comma)
            lower = lower.apply(two_after_comma)
            return upper, middle, lower
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_bollinger_bands", e.__str__())
            return pd.Series(), pd.Series(), pd.Series()

    def calculate_adx(self, f: pd.DataFrame) -> pd.Series:
        try:
            adx = talib.ADX(f['High'], f['Low'], f['Close'])
            result = adx.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_adx", e.__str__())
            return pd.Series()

    def calculate_obv(self, f: pd.DataFrame) -> pd.Series:
        try:
            obv = talib.OBV(f['Close'], f['Volume'])
            result = obv.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_obv", e.__str__())
            return pd.Series()

    def calculate_chakin_oscilator(self, f: pd.DataFrame) -> pd.Series:
        try:
            chakin = talib.ADOSC(f['High'], f['Low'], f['Close'], f['Volume'])
            result = chakin.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_chakin_oscilator", e.__str__())
            return pd.Series()

    def calculate_williams_r(self, f: pd.DataFrame) -> pd.Series:
        try:
            willr = talib.WILLR(f['High'], f['Low'], f['Close'])
            result = willr.apply(two_after_comma)
            return result
        except Exception as e:
            Logger.add_log_error(self.class_name, "calculate_williams_r", e.__str__())
            return pd.Series()

    def refresh_last_row(self):
        try:
            data = pd.read_csv(FileEnums.CSV_FILE.value)
            if self.is_last_kline_past(int(data.iloc[-1]['CloseTime'])):
                self.add_new_row()

                if self.positionContext.get_state() == 'WaitingPositionState':
                    self.positionContext.AlertThings()
            else:
                lastKline = self.get_last_kline()
                data = self.initialize_last_row(data, lastKline)
                data.to_csv(FileEnums.CSV_FILE.value, index=False)
                time.sleep(0.1)
                self.initilaze_all_indicators()
                if self.positionContext.get_state() != 'WaitingPositionState':
                    self.positionContext.AlertThings()
        except Exception as e:
            Logger.add_log_error(self.class_name, "refresh_last_row", e.__str__())
            return self.refresh_last_row()

    def initilaze_all_indicators(self, dataLength: Optional = None):
        if dataLength:
            # this is not working I tried sending last 50 value and try to get last 50 rsi value it should work but calculations are coming wrong
            f = pd.read_csv(FileEnums.CSV_FILE.value).iloc[-dataLength:]
            rsi = self.calculate_rsi(f).iloc[-2:]
            macdHolder = self.calculate_macd(f)
            macd, macdsignal, macdhist = macdHolder[0].iloc[-1], macdHolder[1].iloc[-1], macdHolder[2].iloc[-1]
            stochHolder = self.calculate_stoch(f)
            k, d = stochHolder[0].iloc[-1], stochHolder[1].iloc[-1]
            sar = self.calculate_sar(f).iloc[-1]
            del f
            f = pd.read_csv(FileEnums.CSV_FILE.value)
            f.at[f.index[-1], 'RSI'] = rsi
            f.at[f.index[-1], 'MACD'] = macd
            f.at[f.index[-1], 'MACDSIGNAL'] = macdsignal
            f.at[f.index[-1], 'MACDHIST'] = macdhist
            f.at[f.index[-1], 'STOCHK'] = k
            f.at[f.index[-1], 'STOCHD'] = d
            f.at[f.index[-1], 'SAR'] = sar
        else:
            f = pd.read_csv(FileEnums.CSV_FILE.value)
            f['RSI'] = self.calculate_rsi(f)
            macd, macdsignal, macdhist = self.calculate_macd(f)
            k, d = self.calculate_stoch(f)
            sar = self.calculate_sar(f)
            upper, middle, lower = self.calculate_bollinger_bands(f)
            atr = self.calculate_atr(f)
            willr = self.calculate_williams_r(f)
            chakin = self.calculate_chakin_oscilator(f)
            obv = self.calculate_obv(f)
            adx = self.calculate_adx(f)
            ema200 = self.calculate_ema(f, 200)
            ema100 = self.calculate_ema(f, 100)
            ema50 = self.calculate_ema(f, 50)
            f['MACD'] = macd
            f['MACDSIGNAL'] = macdsignal
            f['MACDHIST'] = macdhist
            f['STOCHK'] = k
            f['STOCHD'] = d
            f['SAR'] = sar
            f['EMA200'] = ema200
            f['EMA100'] = ema100
            f['EMA50'] = ema50
            f['UPPERBBANDS'] = upper
            f['MIDDLEBBANDS'] = middle
            f['LOWERBBANDS'] = lower
            f['ATR'] = atr
            f['WILLR'] = willr
            f['CHAKIN'] = chakin
            f['OBV'] = obv
            f['ADX'] = adx
        f.to_csv(FileEnums.CSV_FILE.value, index=False)

    def add_new_row(self):
        try:
            time.sleep(0.1)
            newKline = self.get_last_kline()
            data = pd.read_csv(FileEnums.CSV_FILE.value)
            oldKline = self.get_last_kline(timeMinute=2)
            data = self.initialize_last_row(data, oldKline)
            data.to_csv(FileEnums.CSV_FILE.value, index=False)
            with open(FileEnums.CSV_FILE.value, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(newKline)
                f.close()
            time.sleep(0.1)
            self.initilaze_all_indicators()
        except Exception as e:
            Logger.add_log_error(self.class_name, "add_new_row", e.__str__())
            self.add_new_row()

    def initialize_last_row(self, df: pd.DataFrame, kline: pd.Series) -> pd.DataFrame:
        try:
            df.at[df.index[-1], 'Open'] = kline[1]
            df.at[df.index[-1], 'High'] = kline[2]
            df.at[df.index[-1], 'Low'] = kline[3]
            df.at[df.index[-1], 'Close'] = kline[4]

            return df
        except Exception as e:
            Logger.add_log_error(self.class_name, "initialize_last_row", e.__str__())
            return self.initialize_last_row(df, kline)

    def is_last_kline_past(self, last_kline_close_time: int) -> bool:
        try:
            return get_current_time_timestamp() > last_kline_close_time
        except Exception as e:
            Logger.add_log_error(self.class_name, "is_last_kline_past", e.__str__())
            return self.is_last_kline_past(last_kline_close_time)

    def is_csv_lines_greater_than(self, value) -> bool:
        try:
            df = pd.read_csv(FileEnums.CSV_FILE.value)
            return len(df) > value
        except Exception as e:
            Logger.add_log_error(self.class_name, "is_csv_lines_greater_than", e.__str__())
            return self.is_csv_lines_greater_than(value)
