from common.db import dbconnector
from utils.logger import logger
from common.config import schema_table_setting

class LoadPostgres:
    def __init__(self):
        self.schemaname=schema_table_setting.PRESTG_SCHEMANAME
        self.tablename =schema_table_setting.PRESTG_TABLENAME
    def load(self, jobs):
        try:
            with dbconnector.connect_Postgres() as conn:
                cursor = conn.cursor()
                sql = f"""
                INSERT INTO {self.schemaname}.{self.tablename} (
                    id, title, company, description, location, country,
                    employment_type, salary_min, salary_max, currency,
                    skills, source, apply_url, posted_date
                )
                VALUES (
                    %(id)s, %(title)s, %(company)s, %(description)s, %(location)s, %(country)s,
                    %(employment_type)s, %(salary_min)s, %(salary_max)s, %(currency)s,
                    %(skills)s, %(source)s, %(apply_url)s, %(posted_date)s
                )
                """

                cursor.executemany(sql, jobs)
                conn.commit()
                cursor.close()
        except Exception as e:
            logger.error(f"Failed to load prestg {e}")