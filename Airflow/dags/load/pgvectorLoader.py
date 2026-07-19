from utils.embedder import embedder
from psycopg2.extras import execute_values
from common.config import schema_table_setting
from common.db import dbconnector
from utils.logger import logger

class LoadVector:
    def __init__(self):
        self.pgconn = dbconnector.connect_Postgres()
        self.stg_table = schema_table_setting.STG_TABLENAME
        self.stg_schema = schema_table_setting.STG_SCHEMANAME
        self.stg_log = schema_table_setting.STG_LOG_TABLENAME
        self.log_schema = schema_table_setting.LOG_SCHEMANAME
        self.vector_log = schema_table_setting.EMBEDDING_LOG_TABLENAME   
        self.vectordb = dbconnector.connect_vectordb()
        self.vectorSchema = schema_table_setting.VECTOR_SCHEMANAME
        self.vectorTable = schema_table_setting.VECTOR_TABLENAME
        
    def load(self):
        try:
            with self.pgconn as conn:
                cur = conn.cursor()
                # Fetch latest records that are not embedded yet
                cur.execute(f"""
                    SELECT id, title, description
                    FROM {self.stg_schema}.{self.stg_table}
                    WHERE createdon > (SELECT COALESCE(
                        MAX(starttime) - INTERVAL '5 minutes',
                        TIMESTAMP '1970-01-01'
                    )
                    FROM {self.log_schema}.{self.vector_log}
                    WHERE status = 'success'
                    )
                """)

                rows = cur.fetchall()

                if not rows:
                    return

                # vector_data = []

                for row in rows:
                    doc_id, title, description = row
                    vector = embedder.embed(description)

                    vector_data = [(
                        (
                            doc_id,
                            title,
                            vector
                        )
                    )]
                # Insert into pgvector table
                    self.status = self.load_db(vector_data)
                conn.commit()
                cur.close()
            logger.info("loading the row to vector completed")
            return self.status
        except Exception as e:
            logger.error(f"failed to load the vector {e}")
            return False
            
    def load_db(self, vector_data):
        try:
            with self.vectordb as vectordbconn:
                cursor = vectordbconn.cursor()
                execute_values(
                    cursor,
                    f"""
                    INSERT INTO {self.vectorSchema}.{self.vectorTable}
                    (jobid, title, embedding)
                    VALUES %s
                    """,
                    vector_data
                )
                vectordbconn.commit()
                cursor.close()
            return True
        except Exception as e:
            logger.error(f"failed to load_db vector {e}")
            return False