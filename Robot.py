import ClientData
from Account.Account import Account
from Data import DataManagement
from Database.Database import Database
from BacktestingModule.Backtesting import Backtest
from BacktestingModule import Backtesting
if __name__ == '__main__':
    database = Database.getInstance()
    database.create_tables()
    print("Lütfen Yapmak İstediğiniz İşlemi Seçiniz")
    print("1 - Backtestingi Çalıştır")
    print("2 - Algoritmik Tradingi Çalıştır")

    get_user_activity = input()
    if get_user_activity == "1":
        a = Backtest("1MinuteData5Year.csv",
                     Backtesting.enterConditions2,
                     Backtesting.exitConditions2)
    if get_user_activity == "2":
        account = Account()
        dm = DataManagement.DataManagement()
        dm.initilaze_all_data()
        dm.initilaze_all_indicators()

        while True:
            dm.refresh_last_row()
