import time

import ClientData
import PositionStates.PositionContext
import PositionStates.WaitingPositionState
from Account.Account import Account
from Account.Order.LongOrderExit import LongOrderExit
from PositionStates.PositionState import PositionState
from StrategyFunctions import StrategyFunctions as Sf


class LongPositionState(PositionState):
    def CheckPosition(self, context):
        acc = Account.getInstance()

        def GetOutOfPosition(pMessage: str):
            print(pMessage, time.ctime(), "Price : ", ClientData.marginLastPosition)
            LongOrderExit().Execute()
            context.set_state(PositionStates.WaitingPositionState.WaitingPositionState())
