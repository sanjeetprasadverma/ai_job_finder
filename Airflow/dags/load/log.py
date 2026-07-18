from common.db import dbconnector
from common.config import schema_table_setting

def insert_log(tablename, jobstarttime, starttime, endtime, status, schemaname=schema_table_setting.LOG_SCHEMANAME):
    with dbconnector.connect_Postgres() as conn:
            cursor = conn.cursor()
            sql = f"""
            INSERT INTO {schemaname}.{tablename} 
            (jobstarttime, starttime, endtime, status)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(sql, (jobstarttime, starttime, endtime, status))
            conn.commit()
            cursor.close()