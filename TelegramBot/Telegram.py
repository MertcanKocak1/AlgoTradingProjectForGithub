from telegram.ext import Updater

import ClientData
from Logger.Logger import Logger
from ConfigManager import ConfigManager


class TelegramBot:
    __instance = None

    def __init__(self):
        if TelegramBot.__instance is not None:
            raise Exception('This Class Singleton!')
        else:
            config = ConfigManager()
            self.updater = Updater(config.telegram_bot_api_key, use_context=True)
            self.chatId = config.my_user_id
            self.dispatcher = self.updater.dispatcher
            self.className = "TelegramBot"
            TelegramBot.__instance = self

    @staticmethod
    def getInstance():
        if TelegramBot.__instance is None:
            TelegramBot()
        return TelegramBot.__instance

    def send_message_to_user(self, text, chat_id=None) -> None:
        if chat_id is None:
            chat_id = self.chatId
        try:
            self.updater.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            Logger.add_log_error(self.className, "send_message_to_user", e.__str__())
