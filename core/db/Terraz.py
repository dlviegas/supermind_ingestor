import psycopg2
from decouple import config
import pandas as pd

class TerrazDB:

    def __init__(self):
        self.__host = config('TERRAZ_HOST')
        self.__user = config('TERRAZ_USER')
        self.__pwd = config('TERRAZ_PWD')
        self.__database = config('TERRAZ_DB')
        self.conn = None

    def _init_conn(self):
        if not self.conn:
            self.conn = psycopg2.connect(
                host=self.__host,
                database=self.__database,
                user=self.__user,
                password=self.__pwd
            )

    def query_to_pandas(self, query_str):
        self._init_conn()
        cursor = self.conn.cursor()
        cursor.execute(query_str)
        result = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        return pd.DataFrame(result, columns=colnames)




