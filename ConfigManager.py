import json


class ConfigManager:
    def __init__(self):
        self.api_key = ""
        self.api_secret = ""
        self.telegram_bot_api_key = ""
        self.my_user_id = ""
        self.database_user = ""
        self.database_password = ""
        self.database_host = ""
        self.database_port = ""
        self.database_name = ""
        self.load_config()

    def load_config(self):
        with open("config.json") as config_file:
            config = json.load(config_file)

        self.api_key = config["API_KEY"]
        self.api_secret = config["SECRET_API_KEY"]
        self.telegram_bot_api_key = config["TELEGRAM_API_KEY"]
        self.my_user_id = config["TELEGRAM_MY_USER_ID"]
        self.database_user = config["DATABASE_USER"]
        self.database_name = config["DATABASE_NAME"]
        self.database_password = config["DATABASE_PASSWORD"]
        self.database_host = config["DATABASE_HOST"]
        self.database_port = config["DATABASE_PORT"]
