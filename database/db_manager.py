import pymysql

import config

sql_config = config.MysqlConfig()


class DBManager(object):
    def __init__(self):
        self.conn = pymysql.connect(
            host=sql_config.host,
            port=sql_config.port,
            user=sql_config.user,
            password=sql_config.pwd,
        )
        self.cursor = self.conn.cursor()
        self.check_init()

    def check_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students ()
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions ()
        """)

    def check_init(self):
        self.cursor.execute("SELECT SCHEMA_NAME FROM information_schema.schemata WHERE SCHEMA_NAME = %s",
                            (sql_config.db,))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute(
                "SELECT TABLE_NAME FROM information_schema.tables WHERE TABLE_SCHEMA = %s",
                (sql_config.db,)
            )
            result = self.cursor.fetchall()
        else:
            self.cursor.execute("CREATE SCHEMA %s", (sql_config.db,))
        self.check_table()
