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
        self.check_table()

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
            y2 int
        )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
            class_id VARCHAR(30),
            date DATETIME,
            duration int
        )
        """)

    def check_init(self):
        self.cursor.execute("SELECT SCHEMA_NAME FROM information_schema.schemata WHERE SCHEMA_NAME = %s",
                            (sql_config.db,))
        result = self.cursor.fetchone()
        if not result:
            self.cursor.execute(f"CREATE DATABASE {sql_config.db}")
        self.conn.select_db(sql_config.db)

    def insert_action(self, data):
        insert_query = """
            INSERT INTO actions (id, class_id, datetime, action, timestamp, x1, y1, x2, y2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.executemany(insert_query, data)
        except Exception as e:
            print(e)

        self.conn.commit()

    def insert_class(self, class_id, date, duration):
        insert_query = """
        INSERT INTO classes (class_id, date,duration)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(insert_query, [class_id, date, duration])
        self.conn.commit()

    def get_students(self):
        self.cursor.execute("SELECT id,name,email FROM students")
        result = self.cursor.fetchall()

        return [_ for _ in result]

    def get_actions(self, name_id, class_id):
        self.cursor.execute("SELECT action, timestamp FROM actions WHERE id = %s AND class_id = %s",
                            (name_id, class_id))
        result = self.cursor.fetchall()
        return list(result)

    def get_class_info(self, class_id, date):
        self.cursor.execute("SELECT class_id,duration,date FROM classes WHERE class_id = %s AND date = %s", (class_id, date))
        result = self.cursor.fetchall()
        return list(result[0])
