import psycopg2
from .config import postgres_setting, pgvector_setting

class DBConnector():
    def __init__(self):
        self.host=postgres_setting.HOST
        self.port=postgres_setting.PORT
        self.dbname=postgres_setting.DBNAME
        self.user=postgres_setting.USER
        self.password=postgres_setting.PASSWORD
    
    def connect_Postgres(self):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )
        return conn
    
    def connect_vectordb(self):
        conn = psycopg2.connect(
            host=pgvector_setting.HOST,
            port=pgvector_setting.PORT,
            dbname=pgvector_setting.DBNAME,
            user=pgvector_setting.USER,
            password=pgvector_setting.PASSWORD,
        )
        return conn
    
dbconnector = DBConnector()