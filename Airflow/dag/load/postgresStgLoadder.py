from common.db import dbconnector
from utils.logger import logger
from common.config import schema_table_setting

class LoadSTGPostgres:
    def __init__(self):
        self.schemaname=schema_table_setting.STG_SCHEMANAME
        self.tablename =schema_table_setting.STG_TABLENAME
        self.prestg_tablename =schema_table_setting.PRESTG_TABLENAME
        self.prestg_schemaname =schema_table_setting.PRESTG_SCHEMANAME
        self.log_schema =schema_table_setting.LOG_SCHEMANAME
        self.stg_log_table =schema_table_setting.STG_LOG_TABLENAME
    def load(self):
        try:
            with dbconnector.connect_Postgres() as conn:
                cursor = conn.cursor()
                sql=f"""WITH last_load AS (
                    SELECT COALESCE(MAX(jobstarttime), '1970-01-01') AS max_time
                    FROM {self.log_schema}.{self.stg_log_table}
                ),
                latest_jobs AS (
                    SELECT DISTINCT ON (id) *
                    FROM {self.prestg_schemaname}.{self.prestg_tablename} p
                    CROSS JOIN last_load l
                    WHERE p.load_time > l.max_time
                    ORDER BY id, load_time DESC
                )
                INSERT INTO {self.schemaname}.{self.tablename} (
                        id,title,company,description,location,country,employment_type,salary_min,salary_max,currency,skills,source,apply_url,posted_date,createdon,modifiedon
                    )
                    SELECT  p.id, p.title, p.company, p.description,  p.location, p.country, p.employment_type, p.salary_min, p.salary_max, p.currency, p.skills, p.source,  p.apply_url,  p.posted_date, CURRENT_TIMESTAMP,  CURRENT_TIMESTAMP
                    FROM latest_jobs p
                    ON CONFLICT (id) 
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        description = EXCLUDED.description,
                        location = EXCLUDED.location,
                        country = EXCLUDED.country,
                        employment_type = EXCLUDED.employment_type,
                        salary_min = EXCLUDED.salary_min,
                        salary_max = EXCLUDED.salary_max,
                        currency = EXCLUDED.currency,
                        skills = EXCLUDED.skills,
                        source = EXCLUDED.source,
                        apply_url = EXCLUDED.apply_url,
                        posted_date = EXCLUDED.posted_date,
                        modifiedon = CURRENT_TIMESTAMP
                        """
                cursor.execute(sql)
                conn.commit()
                cursor.close()
            logger.info("Stg load is completed successfully")
            return True
        except Exception as e:
            logger.error(f"Stg load failed: {e}")
            return False