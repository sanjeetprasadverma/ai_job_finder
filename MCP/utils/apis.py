from common.db import dbconnector
from common.config import schema_table_setting
from common.embedder import embedder
from common.logger import mcp_logger

def get_jobs_db(params, page=1, pagesize = 10, distance=0.4):
    try:
        page= int(page)
        pagesize=int(pagesize)
        distance=float(distance)
        embeded_text = embedder.embed(params)
        offset = (page - 1) * pagesize
        with dbconnector.connect_vectordb() as conn:
            cursor = conn.cursor()
            sql = f"""
            SELECT 
            jobid 
            ,embedding <-> %s::vector AS distance
            FROM {schema_table_setting.VECTOR_SCHEMANAME}.{schema_table_setting.VECTOR_TABLENAME} 
            WHERE embedding <-> %s::vector > %s
            ORDER BY distance ASC, posted_date DESC
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (embeded_text, embeded_text, distance, pagesize, offset))
            matches = cursor.fetchall()
            job_ids = [row[0] for row in matches]
            conn.commit()
            cursor.close()
        if(len(job_ids)==0):
            return {"status":200, "message":"No more jobs found"}
        with dbconnector.connect_Postgres() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["%s"] * len(job_ids))
            sql = f"""
            SELECT *
            FROM {schema_table_setting.STG_SCHEMANAME}.{schema_table_setting.STG_TABLENAME}
            WHERE id IN ({placeholders})
            """
            cursor.execute(sql, job_ids)
            jobs = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            result = [
                dict(zip(columns, row))
                for row in jobs
            ]

            conn.commit()
            cursor.close()
        mcp_logger.info(f"get_jobs_db sending results")
        return {"status":200, "message":result}
    except Exception as e:
        # traceback.print_exc()
        mcp_logger.error(f"get_jobs_db: Error occurred while fetching jobs for query '{params}': {str(e)}")
        return ({"status":500, "message":str(e)})