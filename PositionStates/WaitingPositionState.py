import ClientData
import PositionStates.LongPositionState
import PositionStates.PositionContext
import PositionStates.ShortPositionState
import PositionStates.SpotPositionState
from Account.Order.SpotOrders.SpotOrder import SpotOrder
from PositionStates.PositionState import PositionState
from TelegramBot.Telegram import TelegramBot
import Enums.EnterExitConditions as exc
import StrategyFunctions.StrategyFunctions as sf
from Enums.TradingEnums import TradingEnums
import pandas as pd
from Enums.FileEnums import FileEnums


class WaitingPositionState(PositionState):

    def CheckPosition(self, context):
        # Tamamını okuması hiç iyi değil Belki strategy fonksiyonları içinde bir max değeri alma olur onun üzerinden hesaplanır.
        df = pd.read_csv(FileEnums.CSV_FILE.value)
        i = len(df)
        for strategy in exc.enterConditions:
            metConditionCount = 0
            conditionList = exc.enterConditions[strategy][TradingEnums.FUNCTIONS.value]
            for condition in conditionList:
                rowCount = sf.getRowCount(condition['FunctionName'])
                func = getattr(sf, condition['FunctionName'])
                print(condition)
                # Kapatma Onayı alması için i - 1 gönderiliyor.
                # Başlangıç olarak da i - rowCount - 1 gönderiliyor. Böylece 2 satır gönderdiğimizde tek satır değil 2 satır gitmesi sağlandı.
                if func(df.iloc[i - rowCount - 1: i - 1], *condition['FunctionParameters']):
                    metConditionCount += 1
                    print(metConditionCount)
                    print("len of conditions list", len(conditionList))
            if metConditionCount == len(conditionList):
                print("log waiting for position state entry")
                SpotOrder().create_new_spot_order("BUY")
                ClientData.currentStrategyName = strategy
                context.set_state(PositionStates.SpotPositionState.SpotPositionState())

        # <editor-fold desc="Old Code1">

        """if sf.IsSARCrossUnder():
            print("SAR Aşağıdan Yukarıya Geçti")
            

        if sf.IsRsiLowerThan(40):
            print("Long 1. Worked RSI < 40", time.ctime())
            if sf.IsStochDLowerThan(20) and sf.getInstance().IsStochCrossUnder():
                print("Long 2. Worked D < 20 AND SU", time.ctime())
                if sf.IsMacdTurnedGreener() or sf.isMacdTurnedSoftRedder():
                    LongOrderEntry().Execute()
                    print("Long 3. Worked MGREENER OR SOFTREDDER", time.ctime(), "And Last Price : ",
                          ClientData.marginLastPosition)
                    context.set_state(PositionStates.LongPositionState.LongPositionState())
                    return
        if sf.IsRsiHigherThan(60):
            print("Short 1. Worked RSI > 60", time.ctime())
            if sf.IsStochDHigherThan(80) and sf.IsStochCrossOver():
                print("Short 2. Worked D > 80 AND CO", time.ctime())
                if sf.isMacdTurnedRedder():
                    ShortOrderEntry().Execute()
                    print("3. Worked MREDDER", time.ctime(), "And Last Price : ", ClientData.marginLastPosition)
                    context.set_state(PositionStates.ShortPositionState.ShortPositionState())
                if sf.isMacdTurnedSoftGreener():
                    ShortOrderEntry().Execute()
                    print("3. Worked SoftGreener", time.ctime(), "And Last Price : ", ClientData.marginLastPosition)
                    context.set_state(PositionStates.ShortPositionState.ShortPositionState())
                    return
                """
        # </editor-fold>
