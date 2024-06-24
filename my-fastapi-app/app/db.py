
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# fix url
URL_DATABASE = 'mysql+mysqlconnector://root:Ordenador1/@localhost:3306/BlogApplication'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

'''
import mysql.connector
class Database:
    def __init__(self):
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password",
            database="your_database"
        )

    def disconnect(self):
        if self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.fetchall()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            cursor.close()

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.execute_query(query)

    def drop_table(self, table_name):
        query = f"DROP TABLE IF EXISTS {table_name}"
        self.execute_query(query)

    def insert_data(self, table_name, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.execute_query(query, tuple(data.values()))

    def select_data(self, table_name, columns=None):
        if columns:
            columns = ', '.join(columns)
        else:
            columns = '*'
        query = f"SELECT {columns} FROM {table_name}"
        return self.execute_query(query)

    def update_data(self, table_name, data, condition):
        set_values = ', '.join([f"{column} = %s" for column in data.keys()])
        query = f"UPDATE {table_name} SET {set_values} WHERE {condition}"
        self.execute_query(query, tuple(data.values()))

    def delete_data(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_query(query)
'''