import time

import ClientData
import PositionStates.PositionContext
import PositionStates.WaitingPositionState
from Account.Account import Account
from Account.Order.ShortOrderExit import ShortOrderExit
from PositionStates.PositionState import PositionState


class ShortPositionState(PositionState):
    def CheckPosition(self, context):
        acc = Account.getInstance()

        def GetOutOfPosition(pMessage: str):
            print(pMessage, time.ctime(), "Price : ", ClientData.marginLastPosition)
            ShortOrderExit().Execute()
            context.set_state(PositionStates.WaitingPositionState.WaitingPositionState())
