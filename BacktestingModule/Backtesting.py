import pandas as pd
import numpy as np
from typing import List, Optional
import datetime
import traceback
from Enums.TradingEnums import TradingEnums
import BacktestingModule.ReadyToUseStrategyParams as rtusp
import csv
from Database.Database import Database
import StrategyFunctions.StrategyFunctions as sf
# todo burada sadece and var bunları birer dict dictin valuesuna array verip isimlendirmek daha iyi olabilir
# hashmap içerisinde bir liste tanımlayacağız. Key strateji ismi olacak.

enterConditions2 = {
    'Eclipse12': {
        TradingEnums.FUNCTIONS.value: [rtusp.SAR_CROSS_UNDER,
                                       rtusp.IS_EMA50_LOWER_THAN_CLOSE,
                                       rtusp.STOTASTIC_VALUE_LOWER
                                       ],
        TradingEnums.TAKE_PROFIT.value: 0.8,
        TradingEnums.STOP_LOSS.value: 0.8,
    }}

exitConditions2 = {
    'Eclipse12': [[rtusp.SAR_CROSS_OVER, ]]
}


class Backtest:
    def __init__(self, datasetName, enterConditions, exitConditions,
                 startMoney: [Optional] = 10000,
                 startDate: [Optional] = '0',
                 endDate: [Optional] = '0'):
        self.dataset = ReadDataset(datasetName, startDate, endDate)
        self.enterConditions = enterConditions
        self.exitConditions = exitConditions
        self.enterPositionPrice = 0
        self.exitPositionPrice = 0
        self.tradeCount = 0
        self.startMoney = startMoney
        self.isInPosition = False
        self.currentStrategyName = None
        self.stopLoss = 0
        self.takeProfit = 0
        self.currentStrategyId = None
        self.database = Database.getInstance()
        self.StartStrategy()

    def StartStrategy(self):
        for strategy in self.enterConditions:
            if self.database.check_strategy_exists(strategy) > 0:
                print("Strategy exists")
            else:
                self.stopLoss = self.enterConditions[strategy][TradingEnums.STOP_LOSS.value]
                self.takeProfit = self.enterConditions[strategy][TradingEnums.TAKE_PROFIT.value]
                self.currentStrategyName = strategy
                strategy_id = self.database.add_strategy(strategy, self.enterConditions[strategy],
                                                         self.exitConditions[strategy])
                if strategy_id is not None:
                    self.currentStrategyId = strategy_id
                    for i in range(3, len(self.dataset) - 5):
                        if not self.isInPosition:
                            self.in_position_actions(strategy, i)
                        else:
                            self.out_of_position_actions(strategy, i)
                    self.resetData()

    def in_position_actions(self, strategy, i):
        metConditionCount = 0
        conditionList = self.enterConditions[strategy][TradingEnums.FUNCTIONS.value]
        for condition in conditionList:
            rowCount = getRowCount(condition['FunctionName'])
            func = getattr(sf, condition['FunctionName'])
            if func(self.dataset.iloc[i - rowCount: i], *condition['FunctionParameters']):
                metConditionCount += 1
        if metConditionCount == len(conditionList):
            self.enterPosition(self.dataset.iloc[i])

    def out_of_position_actions(self, strategy, i):
        if TradingEnums.TAKE_PROFIT.value in self.enterConditions[strategy]:
            if self.checkForTakeProfit(self.dataset.iloc[i]):
                self.closePosition(TradingEnums.TAKE_PROFIT.value, self.dataset.iloc[i])
                return
        if TradingEnums.STOP_LOSS.value in self.enterConditions[strategy]:
            if self.checkForStopLoss(self.dataset.iloc[i]):
                self.closePosition(TradingEnums.STOP_LOSS.value, self.dataset.iloc[i])
                return
        conditions = self.exitConditions[strategy]
        metConditionCount = 0
        for conditionList in conditions:
            for condition in conditionList:
                rowCount = getRowCount(condition['FunctionName'])
                func = getattr(sf, condition['FunctionName'])
                if func(self.dataset.iloc[i - rowCount: i], *condition['FunctionParameters']):
                    metConditionCount += 1
                if metConditionCount == len(conditionList):
                    self.closePosition(condition['FunctionName'], self.dataset.iloc[i])
                    break

    def resetData(self):
        self.enterPositionPrice = 0
        self.exitPositionPrice = 0
        self.tradeCount = 0
        self.startMoney = 10000
        self.isInPosition = False
        self.currentStrategyName = None
        self.stopLoss = 0
        self.takeProfit = 0

    # Stop Loss Take Profit functions    -----------------------------------
    def checkForStopLoss(self, row):
        return row['Low'] < self.enterPositionPrice - ((self.enterPositionPrice / 100) * self.stopLoss)

    def checkForTakeProfit(self, row):
        return row['High'] > self.enterPositionPrice + ((self.enterPositionPrice / 100) * self.takeProfit)

    def closePosition(self, reason, row):
        if reason == TradingEnums.TAKE_PROFIT.value:
            self.exitPositionPrice = self.enterPositionPrice + ((self.enterPositionPrice / 100) * self.takeProfit)
            self.startMoney += (self.startMoney / 100) * self.takeProfit
        elif reason == TradingEnums.STOP_LOSS.value:
            self.startMoney -= (self.startMoney / 100) * self.stopLoss
            self.exitPositionPrice = self.enterPositionPrice - ((self.enterPositionPrice / 100) * self.stopLoss)
        elif reason != TradingEnums.STOP_LOSS.value or reason != TradingEnums.TAKE_PROFIT.value:
            self.exitPositionPrice = row['Close']
            self.startMoney *= (self.exitPositionPrice / self.enterPositionPrice)
        self.tradeCount += 1
        self.isInPosition = not self.isInPosition
        self.database.add_position_detail(self.currentStrategyId, self.enterPositionPrice, self.exitPositionPrice,
                                          self.startMoney, reason, self.tradeCount)
        self.addPositionRow(row)
        self.enterPositionPrice = 0
        self.exitPositionPrice = 0

    def enterPosition(self, row):
        self.isInPosition = not self.isInPosition
        self.tradeCount += 1
        self.enterPositionPrice = row['Close']
        self.database.add_position_detail(self.currentStrategyId, self.enterPositionPrice, self.exitPositionPrice,
                                          self.startMoney, 'Enter Position', self.tradeCount)
        self.addPositionRow(row)

    def addPositionRow(self, row):
        row = row.to_json().__str__()
        self.database.add_row_position_detail(self.currentStrategyId, row, self.tradeCount)

def ReadDataset(name, startDate, endDate):
    try:
        df = pd.read_csv(name).iloc[2000000:]
        if isUnixTimeInMs(df['OpeningTime'].iloc[-1]):
            df = UnixToDate(df, ['OpeningTime', 'CloseTime'])
        if endDate == '0':
            endDate = df.iloc[-1]['CloseTime']
        df = df.loc[(df['OpeningTime'] >= startDate) & (df['CloseTime'] <= endDate)]
        df = df.dropna()
        df.reset_index(inplace=True, drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


# Gets the number of rows needed for the function
def getRowCount(functionName):
    try:
        return next((key for key, value in sf.functionsAndRowCounts.items() if functionName in value))
    except StopIteration:
        # If the given function name is not found in functionsAndRowCounts, return None.
        return None


# Time functions    -----------------------------------
def isUnixTimeInMs(time):
    try:
        datetime.datetime.fromtimestamp(time / 1000.0)
        return True
    except (ValueError, OSError):
        return False


def UnixToDate(df, columns):
    try:
        for column in columns:
            df[column] = pd.to_datetime(df[column], unit='ms', utc=True).dt.tz_convert('Etc/GMT-3').dt.strftime(
                "%Y/%m/%d %H:%M:%S")
        return df
    except Exception as e:
        traceback.print_exc()
