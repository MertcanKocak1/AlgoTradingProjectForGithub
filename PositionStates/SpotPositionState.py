import time

import PositionStates.PositionContext
import PositionStates.WaitingPositionState
from Account.Account import Account
from Account.Order.SpotOrders.SpotOrder import SpotOrder
from PositionStates.PositionState import PositionState
import pandas as pd
from Enums.FileEnums import FileEnums
import Enums.EnterExitConditions as eec
from Enums.TradingEnums import TradingEnums
import ClientData
import StrategyFunctions.StrategyFunctions as sf


class SpotPositionState(PositionState):
    def CheckPosition(self, context):
        acc = Account.getInstance()
        # Tamamını okuması hiç iyi değil Belki strategy fonksiyonları içinde bir max değeri alma olur onun üzerinden hesaplanır.
        df = pd.read_csv(FileEnums.CSV_FILE.value)
        i = len(df)
        print("spot position state")

        def GetOutOfPosition(pMessage: str):
            SpotOrder().create_new_spot_order("SELL")
            print(pMessage, time.ctime(), "Price : ", acc.get_last_position_price())
            acc.set_last_position_price(0)
            context.set_state(PositionStates.WaitingPositionState.WaitingPositionState())
            ClientData.currentStrategyName = ""

        if TradingEnums.TAKE_PROFIT in eec.enterConditions[ClientData.currentStrategyName]:
            if sf.check_for_take_profit(df, eec.enterConditions[ClientData.currentStrategyName][
                TradingEnums.TAKE_PROFIT.value]):
                print("log spot position tp state exit")
                GetOutOfPosition("TP")
                return
        if TradingEnums.STOP_LOSS in eec.enterConditions[ClientData.currentStrategyName]:
            if sf.check_for_stop_loss(df, eec.enterConditions[ClientData.currentStrategyName][
                TradingEnums.STOP_LOSS.value]):
                print("log spot position sl state exit")
                GetOutOfPosition("SL")
                return
        conditions = eec.exitConditions[ClientData.currentStrategyName]
        metConditionCount = 0
        for conditionList in conditions:
            for condition in conditionList:
                rowCount = sf.getRowCount(condition['FunctionName'])
                func = getattr(sf, condition['FunctionName'])
                if func(df.iloc[i - rowCount - 1: i - 1], *condition['FunctionParameters']):
                    metConditionCount += 1
                if metConditionCount == len(conditionList):
                    print("log spot position condition state exit")
                    GetOutOfPosition("something")
                    break

        # <editor-fold desc="Old Code">

        """
        if sf.IsSARCrossOver():
            GetOutOfPosition("SAR YUKARIYA GEÇTİ")
            return

        
        if acc.get_last_price() > ClientData.spotLastPosition + ((ClientData.spotLastPosition / 100) * 1.02) \
                or acc.get_last_price() < ClientData.spotLastPosition - ((ClientData.spotLastPosition / 100) * 1.02):
            GetOutOfPosition("SL/TP")
            return
        if sf.IsRsiHigherThan(50) and sf.IsStochCrossOver():
            GetOutOfPosition("RSI > 50 and Stoch CO")
            return
        if sf.IsStochDHigherThan(80) and sf.IsStochCrossOver():
            GetOutOfPosition("Stoch D > 80 and Stoch CO")
            return
        if sf.IsRsiHigherThan(70):
            GetOutOfPosition("RSI > 70")
            return
        if sf.IsRsiHigherThan(50) and (sf.isMacdTurnedSoftGreener() or sf.isMacdTurnedRedder()):
            GetOutOfPosition("RSI > 50 and MACD")
            return
        """
        # </editor-fold>
