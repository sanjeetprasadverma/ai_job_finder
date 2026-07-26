from common.db import dbconnector
from common.logger import logger
from common.config import schema_table_setting
from common.embedder import embedder

def get_embedding_dimension():
    test_embedding = embedder.embed("dimension check")
    return len(test_embedding)

def create_table():
    try:
        PRESTG_SCHEMANAME=schema_table_setting.PRESTG_SCHEMANAME
        STG_SCHEMANAME= schema_table_setting.STG_SCHEMANAME
        PRESTG_TABLENAME=schema_table_setting.PRESTG_TABLENAME
        STG_TABLENAME=schema_table_setting.STG_TABLENAME
        LOG_SCHEMANAME=schema_table_setting.LOG_SCHEMANAME
        PRESTG_LOG_TABLENAME=schema_table_setting.PRESTG_LOG_TABLENAME
        STG_LOG_TABLENAME=schema_table_setting.STG_LOG_TABLENAME
        EMBEDDING_LOG_TABLENAME=schema_table_setting.EMBEDDING_LOG_TABLENAME
        VECTOR_SCHEMANAME=schema_table_setting.VECTOR_SCHEMANAME
        VECTOR_TABLENAME=schema_table_setting.VECTOR_TABLENAME
        
        with dbconnector.connect_Postgres() as conn:
            cursor = conn.cursor()
            
            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {PRESTG_SCHEMANAME}
            """
            cursor.execute(sql)
            sql = f"""
            CREATE TABLE IF NOT EXISTS {PRESTG_SCHEMANAME}.{PRESTG_TABLENAME}(
                id TEXT,
                title TEXT,
                company TEXT,
                description TEXT,
                location TEXT,
                country TEXT,
                employment_type TEXT,
                salary_min DOUBLE PRECISION,
                salary_max DOUBLE PRECISION,
                currency VARCHAR(10),
                skills TEXT[] DEFAULT '{{}}',
                source TEXT,
                apply_url TEXT,
                posted_date TIMESTAMP,
                load_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
            """
            cursor.execute(sql)
            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {STG_SCHEMANAME}
            """
            cursor.execute(sql)
            sql = f"""
            CREATE TABLE IF NOT EXISTS {STG_SCHEMANAME}.{STG_TABLENAME}(
                id TEXT UNIQUE NOT NULL,
                title TEXT,
                company TEXT,
                description TEXT,
                location TEXT,
                country TEXT,
                employment_type TEXT,
                salary_min DOUBLE PRECISION,
                salary_max DOUBLE PRECISION,
                currency VARCHAR(10),
                skills TEXT[] DEFAULT '{{}}',
                source TEXT,
                apply_url TEXT,
                posted_date TIMESTAMP,
                createdon TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                modifiedon TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
            """
            cursor.execute(sql)
            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {LOG_SCHEMANAME}
            """
            cursor.execute(sql)
            sql = f"""
            CREATE TABLE IF NOT EXISTS {LOG_SCHEMANAME}.{PRESTG_LOG_TABLENAME}(
                jobstarttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                starttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                endtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR
                    )
            """
            cursor.execute(sql)
            sql = f"""
            CREATE TABLE IF NOT EXISTS {LOG_SCHEMANAME}.{STG_LOG_TABLENAME}(
                jobstarttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                starttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                endtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR
                    )
            """
            cursor.execute(sql)
            sql = f"""
                CREATE INDEX IF NOT EXISTS idx_prestg_load_time
                ON {PRESTG_SCHEMANAME}.{PRESTG_TABLENAME} (load_time);
                """
            cursor.execute(sql)

            sql = f"""
                CREATE INDEX IF NOT EXISTS idx_stg_id
                ON {STG_SCHEMANAME}.{STG_TABLENAME} (id);
                """
            cursor.execute(sql)
            sql = f"""
            CREATE TABLE IF NOT EXISTS {LOG_SCHEMANAME}.{EMBEDDING_LOG_TABLENAME}(
                jobstarttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                starttime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                endtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR
                    )
            """
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        logger.info("table creation completed")
        
        with dbconnector.connect_vectordb() as conn:
            cursor = conn.cursor()
            
            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {VECTOR_SCHEMANAME}
            """
            cursor.execute(sql)
            sql = f"""CREATE EXTENSION IF NOT EXISTS vector"""
            cursor.execute(sql)
            sql = f"""
                CREATE TABLE IF NOT EXISTS {VECTOR_SCHEMANAME}.{VECTOR_TABLENAME} (
                    jobid TEXT,
                    title TEXT,
                    posted_date TIMESTAMP,
                    embedding VECTOR({get_embedding_dimension()}) 
                )"""
            cursor.execute(sql)
            sql = f"""
            CREATE INDEX IF NOT EXISTS {VECTOR_TABLENAME}_embedding_idx
            ON {VECTOR_SCHEMANAME}.{VECTOR_TABLENAME}
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
            """
            cursor.execute(sql)
            conn.commit()
            cursor.close()
        logger.info("vector table creation completed")

    except Exception  as e:
        logger.error(f"failed to create the table {e}")