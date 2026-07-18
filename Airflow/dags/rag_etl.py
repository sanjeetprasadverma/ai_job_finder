from retrieval.retrieve import retriever
from load.loader import Loader
from utils.createtables import create_table
from utils.logger import logger
from load.log import insert_log
from common.config import schema_table_setting
from datetime import datetime
from airflow import DAG
from airflow.decorators import task
from airflow.utils.trigger_rule import TriggerRule

create_table()

default_args={
        'owner': 'airflow',
        'start_date': datetime(2024, 1, 1),
    }

with DAG(
    dag_id="initialize_rag_db",
    schedule="@once",
    catchup=False,
) as dag:

    @task
    def init():
        create_table()

    init()


with DAG(
    dag_id='rag_etl',
    default_args=default_args,
    schedule="*/30 * * * *",
    catchup=False,
) as dag:
    loadder = Loader()
    @task
    def fetch_jobs():
        return retriever.fetch()
    
    @task
    def save_to_prestg_db(batch):
        for jobs in batch:
            loadder.load(jobs)
    
    @task
    def update_stg_db():
        loadder.load_stg()
            
            
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def audit_pipeline(log_table, jobstarttime, starttime, endtime, **args):
        status = "success"

        for value in args.values():
            if not value:
                status = "failed"
                break

        insert_log(log_table, jobstarttime, starttime, endtime, status)
        return status
    
    jobstarttime=datetime.now()
    batch = fetch_jobs()
    starttime = datetime.now()
    save_prestg= save_to_prestg_db(batch)
    logger.info("Prestg load is completed")
    endtime = datetime.now()
    audit_pipeline(schema_table_setting.PRESTG_LOG_TABLENAME, jobstarttime, starttime, endtime, batch=batch,
    save_prestg=save_prestg)
    starttime = datetime.now()
    update_stg = update_stg_db()
    endtime = datetime.now()
    audit_pipeline(schema_table_setting.STG_LOG_TABLENAME, jobstarttime, starttime, endtime, update_stg = update_stg)
