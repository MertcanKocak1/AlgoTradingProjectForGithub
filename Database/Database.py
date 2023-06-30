import psycopg2
import pandas as pd
import json
from ConfigManager import ConfigManager

class Database:
    __instance = None

    def __init__(self):
        if Database.__instance is not None:
            raise Exception('This Class Singleton')
        else:
            config = ConfigManager()
            self.conn = psycopg2.connect(
                database=config.database_name, user=config.database_user, password=config.database_password, host=config.database_host, port=config.database_port
            )
            self.cursor = self.conn.cursor()
            Database.__instance = self

    def escape_quotes(self, value):
        if isinstance(value, str):
            return value.replace("'", "''").replace('"', '\\"')
        return value

    @staticmethod
    def getInstance():
        if Database.__instance is None:
            Database()
        return Database.__instance

    def closeConnection(self):
        self.conn.close()

    # log_class_name : içinde bulunduğu tüm sınıf
    # log_function_name : içinde bulunduğu fonksiyon
    # log_message : log mesajı ; Ekle, Sil vs
    # log_description : log açıklaması
    # is_log_has_error : yapılan işlemde hata dönüp dönmediğini belirtir. True / False
    def create_log(self, log_class_name: str, log_function_name: str, log_message: str, log_description: str,
                   is_log_has_error: bool):
        self.cursor = self.conn.cursor()

        sql_insert_code = '''INSERT INTO log(log_class_name, log_function_name, log_message, log_description, is_log_has_error) 
                             VALUES (%s, %s, %s, %s, %s)'''
        values = (self.escape_quotes(log_class_name), self.escape_quotes(log_function_name),
                  self.escape_quotes(log_message), self.escape_quotes(log_description),
                  self.escape_quotes(is_log_has_error))

        self.cursor.execute(sql_insert_code, values)
        self.conn.commit()

        self.cursor.execute("SELECT LASTVAL()")
        log_id = self.cursor.fetchone()[0]

        return log_id

    # log_id : bağlı olduğu logun id'si
    # log_detail : log detayları
    def create_log_detail(self, log_id: str, log_detail: str):
        self.cursor = self.conn.cursor()
        sql_insert_code = f'''INSERT INTO log_detail(log_id, log_detail) VALUES ('{self.escape_quotes(log_id)}', '{self.escape_quotes(log_detail)}')'''
        self.cursor.execute(sql_insert_code)
        self.conn.commit()

    # api tarafından dönen hataları değil kod tarafında olan hataları takip etmemizi sağlar.
    # log_function_name : içinde bulunduğu fonksiyon
    # log_description : log açıklaması genellikle Exception e içerisinden e nin değeri.
    def create_log_error(self, log_class_name: str, log_function_name: str, log_description: str):
        self.cursor = self.conn.cursor()
        sql_insert_code = f'''INSERT INTO log_error(log_class_name, log_function_name, log_description) 
                             VALUES ('{self.escape_quotes(log_class_name)}', '{self.escape_quotes(log_function_name)}', '{self.escape_quotes(log_description)}')'''
        self.cursor.execute(sql_insert_code)
        self.conn.commit()

    def create_log_table(self):
        self.cursor = self.conn.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS log
                                (id SERIAL PRIMARY KEY,
                                log_class_name varchar,
                                log_function_name varchar,
                                log_message varchar,
                                log_description TEXT,
                                is_log_has_error BOOLEAN,
                                log_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp)'''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def create_log_detail_table(self):
        self.cursor = self.conn.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS log_detail
                                (id SERIAL PRIMARY KEY,
                                log_id INTEGER,
                                log_detail TEXT,
                                log_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp)'''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def create_log_error_table(self):
        self.cursor = self.conn.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS log_error
                                (id SERIAL PRIMARY KEY,
                                log_function_name varchar,
                                log_class_name varchar,
                                log_description TEXT,
                                log_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp)'''
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def create_strategy_table(self):
        self.cursor = self.conn.cursor()
        create_strategy_table_query = '''create table if not exists strategy_detail(
                        id SERIAL PRIMARY KEY,
                        strategy_name TEXT,
                        enter_conditions TEXT,
                        exit_conditions TEXT,
                        strategy_run_time TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp
                    )'''
        self.cursor.execute(create_strategy_table_query)
        self.conn.commit()

    def create_position_detail_table(self):
        self.cursor = self.conn.cursor()
        create_position_detail_table_query = '''create table if not exists position_detail(
                           id SERIAL PRIMARY KEY,
                           strategy_id INTEGER,
                           enter_position_price float,
                           exit_position_price float,
                           start_money float,
                           reason TEXT, 
                           trade_id INTEGER,
                           position_detail_run_time TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp
                       )'''
        self.cursor.execute(create_position_detail_table_query)
        self.conn.commit()

    def create_row_position_detail_table(self):
        self.cursor = self.conn.cursor()
        create_row_position_detail_table_query = '''create table if not exists row_position_detail(
                           id SERIAL PRIMARY KEY,
                           strategy_id INTEGER,
                           row TEXT,
                           trade_id INTEGER, 
                           row_position_run_time TIMESTAMP WITHOUT TIME ZONE DEFAULT current_timestamp
                       )'''
        self.cursor.execute(create_row_position_detail_table_query)
        self.conn.commit()

    def add_position_detail(self, strategy_id, enter_position_price, exit_position_price, start_money, reason,
                            trade_id):
        self.cursor = self.conn.cursor()
        insert_position_detail_query = '''insert into position_detail (strategy_id, enter_position_price, 
                                         exit_position_price, start_money, reason, trade_id)
                                         values (%s, %s, %s, %s, %s, %s )'''
        self.cursor.execute(insert_position_detail_query, (strategy_id, enter_position_price,
                                                           exit_position_price, start_money, reason, trade_id))
        self.conn.commit()

    def add_row_position_detail(self, strategy_id, row, trade_id):
        self.cursor = self.conn.cursor()
        insert_row_position_detail_query = '''insert into row_position_detail (strategy_id, row, trade_id)
                                              values (%s, %s, %s)'''
        self.cursor.execute(insert_row_position_detail_query, (strategy_id, row, trade_id))
        self.conn.commit()

    def check_strategy_exists(self, strategy_name):
        self.cursor = self.conn.cursor()
        select_strategy_query = '''select count(*) from strategy_detail where strategy_name = %s'''
        self.cursor.execute(select_strategy_query, (strategy_name,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def add_strategy(self, strategy_name, enter_conditions, exit_conditions):
        self.cursor = self.conn.cursor()
        insert_strategy_query = '''INSERT INTO strategy_detail (strategy_name, enter_conditions, exit_conditions) 
                                  VALUES (%s, %s, %s) RETURNING id'''
        self.cursor.execute(insert_strategy_query,
                            (strategy_name, json.dumps(enter_conditions), json.dumps(exit_conditions)))
        strategy_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return strategy_id

    def create_tables(self):
        self.create_log_table()
        self.create_log_detail_table()
        self.create_log_error_table()
        self.create_strategy_table()
        self.create_position_detail_table()
        self.create_row_position_detail_table()

    def CreateSQLQueryToDataFrame(self, queryString: str) -> pd.DataFrame:
        self.cursor = self.conn.cursor()
        self.cursor.execute(queryString)
        column_names = [i[0] for i in self.cursor.description]
        return pd.DataFrame(self.cursor.fetchall(), columns=column_names)
