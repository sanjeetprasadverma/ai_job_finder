import os
from dotenv import load_dotenv
load_dotenv()

def get_env(name:str):
    return os.getenv(name)

class ADZUNA_SETTINGS:
    BASE_URL = os.getenv("ADZUNA_BASE_URL", "https://api.adzuna.com/v1/api/jobs/in/search/")
    APP_ID= get_env('ADZUNA_APPLICATION_ID')
    API_KEY= get_env('ADZUNA_APPLICATION_API_KEY')
    SORT_BY= os.getenv("ADZUNA_SORT_BY",'date')
    MAX_DAYS_OLD= os.getenv("ADZUNA_MAX_DAYS_OLD",'1')
    RESULTS_PER_PAGE= os.getenv("ADZUNA_RESULTS_PER_PAGE",'50')

class POSTGRESS_SETTINGS:
    HOST=get_env("POSTGRESS_HOST")
    PORT=get_env("POSTGRESS_PORT")
    DBNAME=get_env("POSTGRESS_DBNAME")
    USER=get_env("POSTGRESS_USER")
    PASSWORD=get_env("POSTGRESS_PASSWORD")
    
class PGVECTOR_SETTINGS:
    HOST=get_env("VECTORDB_HOST")
    PORT=get_env("VECTORDB_PORT")
    DBNAME=get_env("VECTORDB_DBNAME")
    USER=get_env("VECTORDB_USER")
    PASSWORD=get_env("VECTORDB_PASSWORD")

class EMBEDDING_MODEL:
    trans_model ="all-MiniLM-L6-v2"
    ollama_model ="nomic-embed-text"
    
class SCHEMA_TABLE_SETTINGS:
    PRESTG_SCHEMANAME='PRESTG'
    STG_SCHEMANAME='STG'
    PRESTG_TABLENAME='JOBS'
    STG_TABLENAME='JOBS'
    LOG_SCHEMANAME='LOG_METADATA'
    PRESTG_LOG_TABLENAME='PRESTG_LOG_TABLE'
    STG_LOG_TABLENAME='STG_LOG_TABLE'
    EMBEDDING_LOG_TABLENAME='EMBEDDING_LOG_TABLE'
    VECTOR_SCHEMANAME='VECTOR'
    VECTOR_TABLENAME='JOBS'

adzuna_setting= ADZUNA_SETTINGS()
postgres_setting = POSTGRESS_SETTINGS()
pgvector_setting= PGVECTOR_SETTINGS()
embedding_model = EMBEDDING_MODEL()
schema_table_setting=SCHEMA_TABLE_SETTINGS()