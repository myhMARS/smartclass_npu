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
        CREATE TABLE IF NOT EXISTS students (
            id VARCHAR(30) PRIMARY KEY,
            name VARCHAR(30),
            email VARCHAR(255)
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id VARCHAR(30),
            class_id VARCHAR(30),
            datetime DATETIME,
            action VARCHAR(30),
            timestamp int,
            x1 int,
            y1 int,
            x2 int,
            y2 int,
            FOREIGN KEY (id) REFERENCES students(id)
        )
        """)

    def check_init(self):
        self.cursor.execute("SELECT SCHEMA_NAME FROM information_schema.schemata WHERE SCHEMA_NAME = %s",
                            (sql_config.db,))
        result = self.cursor.fetchone()
        if not result:
            self.cursor.execute(f"CREATE DATABASE {sql_config.db}")
        self.conn.select_db(sql_config.db)
        self.check_table()

    def insert_action(self, data):
        insert_query = """
            INSERT INTO actions (id, class_id, datetime, action, timestamp, x1, y1, x2, y2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_query, data)
        except Exception as e:
            print(e)

        self.conn.commit()
