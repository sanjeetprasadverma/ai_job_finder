from retrieval.retrieve import retriever
from load.loader import Loader
from utils.createtables import create_table
from utils.logger import logger
from load.log import log
from common.config import schema_table_setting
import datetime

jobstarttime=datetime.datetime.now()
create_table()
batch = retriever.fetch()
starttime = datetime.datetime.now()
loadder = Loader()
for jobs in batch:
    loadder.load(jobs)
logger.info("Prestg load is completed")
endtime = datetime.datetime.now()
log(schema_table_setting.PRESTG_LOG_TABLENAME, jobstarttime, starttime, endtime, 'sucess')
starttime = datetime.datetime.now()
loadder.load_stg()
endtime = datetime.datetime.now()
log(schema_table_setting.PRESTG_LOG_TABLENAME, jobstarttime, starttime, endtime, 'sucess')
