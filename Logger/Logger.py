from Database.Database import Database


class Logger:

    @staticmethod
    def add_log(log_class_name: str, log_function_name: str, log_message: str, log_description: str,
                is_log_has_error: bool):
        database = Database.getInstance()
        log_id = database.create_log(log_class_name, log_function_name, log_message, log_description, is_log_has_error)
        return log_id

    @staticmethod
    def add_log_detail(log_id: str, log_detail: str):
        database = Database.getInstance()
        database.create_log_detail(log_id, log_detail)

    @staticmethod
    def add_log_error(log_class_name: str, log_function_name: str, log_description: str):
        database = Database.getInstance()
        database.create_log_error(log_class_name, log_function_name, log_description)
