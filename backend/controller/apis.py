from utils import Response
from common.db import dbconnector
from common.config import schema_table_setting
from common.embedder import embedder
from fastapi.concurrency import run_in_threadpool
from fastapi import Request
import requests
import os
from dotenv import load_dotenv
from common.logger import backend_logger
load_dotenv()
# import traceback
TELEGRAM_TOKEN= os.getenv("TELEGRAM_TOKEN","")
user_search_cache = {}


async def telegram_webhook(request: Request):
    data = await request.json()

    if "message" in data:
        await handle_message(data["message"])
    elif "callback_query" in data:
        await handle_callback(data["callback_query"])

    return {"status": "ok"}


async def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message["text"]

    print("User:", text)
    user_search_cache[chat_id] = text  # remember this search for pagination

    result = await run_in_threadpool(get_jobs, text, 1)
    reply_text = format_reply(result)
    keyboard = build_keyboard(page=1, has_results=is_success(result))

    await send_message(chat_id, reply_text, keyboard)


async def handle_callback(callback):
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]
    callback_id = callback["id"]
    action, page = callback["data"].split(":")  # e.g. "next:2"
    page = int(page)

    text = user_search_cache.get(chat_id)
    if not text:
        await answer_callback(callback_id, "Session expired, please search again.")
        return

    result = await run_in_threadpool(get_jobs, text, page)
    reply_text = format_reply(result)
    keyboard = build_keyboard(page=page, has_results=is_success(result))

    await edit_message(chat_id, message_id, reply_text, keyboard)
    await answer_callback(callback_id)  # stops the loading spinner on the button


def is_success(result):
    return result.get("status") == 200 and isinstance(result.get("message"), list) and result["message"]


def build_keyboard(page, has_results):
    buttons = []
    if page > 1:
        buttons.append({"text": "◀ Prev", "callback_data": f"prev:{page-1}"})
    if has_results:  # only show Next if the current page actually returned results
        buttons.append({"text": "Next ▶", "callback_data": f"next:{page+1}"})
    return {"inline_keyboard": [buttons]} if buttons else None


async def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(url, json=payload)


async def edit_message(chat_id, message_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    requests.post(url, json=payload)


async def answer_callback(callback_id, text=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    requests.post(url, json=payload)
def format_reply(result: dict) -> str:
    if result.get("status") != 200:
        return f"⚠️ Something went wrong: {result.get('message')}"

    jobs = result.get("message")

    if isinstance(jobs, str):
        return jobs

    if not jobs:
        return "No jobs found."

    lines = []
    for job in jobs[:10]:
        title = job.get("title", "Untitled")
        company = job.get("company", "")
        url = job.get("apply_url", "")
        lines.append(f"• {title} — {company}\n{url}")

    return "\n\n".join(lines)

def get_jobs(params, page=1, pagesize = 10, distance=0.4):
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
        return {"status":200, "message":result}
    except Exception as e:
        # traceback.print_exc()
        return ({"status":500, "message":str(e)})