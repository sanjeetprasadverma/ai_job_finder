from retrieval.retrieve import retriever
from load.loader import Loader
from utils.createtables import create_table
from common.logger import airflow_logger as logger
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
    schedule="@daily",
    catchup=False,
) as dag:
    loadder = Loader()
    @task
    def fetch_jobs():
        logger.info("fetching the data")
        return retriever.fetch()
    
    # @task
    # def save_to_prestg_db(batch):
    #     status =True
    #     logger.info("Prestg load started")
    #     for jobs in batch:
    #         status = status and loadder.load(jobs)
    #     logger.info("Prestg load completed")
    #     return status
            
            
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def audit_pipeline(log_table, jobstarttime, starttime, endtime, status):

        insert_log(log_table, jobstarttime, starttime, endtime, status)
        return status
    
    jobstarttime=datetime.now()
    batch = fetch_jobs()
    starttime = datetime.now()
    # save_prestg= save_to_prestg_db(batch)
    endtime = datetime.now()
    # status = "success" if save_prestg ==True and len(batch)> 0 else "failed"
    status = "success" if  batch else "failed"
    audit = audit_pipeline(schema_table_setting.PRESTG_LOG_TABLENAME, jobstarttime, starttime, endtime, status)
    
    # batch >> save_prestg >> audit
    batch >> audit
    
    
with DAG(
    dag_id='stag_load',
    default_args=default_args,
    schedule="@daily",

    catchup=False,
) as dag:
    loadder = Loader()
    @task
    def update_stg_db():
        return loadder.load_stg()
            
            
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def audit_pipeline(log_table, jobstarttime, starttime, endtime, stat):
        status = "success" if stat ==True else "failed"

        insert_log(log_table, jobstarttime, starttime, endtime, status)
        return status
    
    jobstarttime=datetime.now()
    starttime = datetime.now()
    update_stg = update_stg_db()
    endtime = datetime.now()
    audit = audit_pipeline(schema_table_setting.STG_LOG_TABLENAME, jobstarttime, starttime, endtime, update_stg)
    update_stg >> audit
    
    
with DAG(
    dag_id='vector_load',
    default_args=default_args,
    # schedule="0 */12 * * *",
    schedule="@daily",
    catchup=False,
) as dag:
    loadder = Loader()
    @task
    def load_vector():
        return loadder.load_vectorload()
            
            
    @task(trigger_rule=TriggerRule.ALL_DONE)
    def audit_pipeline(log_table, jobstarttime, starttime, endtime, stat):
        status = "success" if stat ==True else "failed"

        insert_log(log_table, jobstarttime, starttime, endtime, status)
        return status
    
    jobstarttime=datetime.now()
    starttime = datetime.now()
    load = load_vector()
    endtime = datetime.now()
    audit = audit_pipeline(schema_table_setting.EMBEDDING_LOG_TABLENAME, jobstarttime, starttime, endtime, load)
    load >> audit
