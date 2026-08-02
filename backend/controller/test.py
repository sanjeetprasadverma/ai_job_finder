# from fastapi import Request
# import requests
# import os

# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

# # chat_id -> {"query": str, "jobs": [...], "index": int, "page": int}
# user_sessions = {}

# PAGE_SIZE = 10
# DESC_LIMIT = 500  # characters, keep cards readable


# async def telegram_webhook(request: Request):
#     data = await request.json()

#     if "message" in data:
#         await handle_message(data["message"])
#     elif "callback_query" in data:
#         await handle_callback(data["callback_query"])

#     return {"status": "ok"}


# async def handle_message(message):
#     chat_id = message["chat"]["id"]
#     text = message["text"]

#     print("User:", text)

#     result = await run_in_threadpool(get_jobs, text, 1, PAGE_SIZE)

#     if result.get("status") != 200 or not isinstance(result.get("message"), list) or not result["message"]:
#         await send_message(chat_id, "No jobs found for that search.")
#         return

#     jobs = result["message"]
#     user_sessions[chat_id] = {"query": text, "jobs": jobs, "index": 0, "page": 1}

#     card, keyboard = build_card(chat_id)
#     await send_message(chat_id, card, keyboard)


# async def handle_callback(callback):
#     chat_id = callback["message"]["chat"]["id"]
#     message_id = callback["message"]["message_id"]
#     callback_id = callback["id"]
#     action = callback["data"]  # "next" or "prev"

#     session = user_sessions.get(chat_id)
#     if not session:
#         await answer_callback(callback_id, "Session expired, please search again.")
#         return

#     if action == "next":
#         if session["index"] + 1 < len(session["jobs"]):
#             session["index"] += 1
#         else:
#             # need to fetch the next page from the DB
#             next_page = session["page"] + 1
#             result = await run_in_threadpool(get_jobs, session["query"], next_page, PAGE_SIZE)
#             new_jobs = result.get("message") if result.get("status") == 200 else None

#             if not isinstance(new_jobs, list) or not new_jobs:
#                 await answer_callback(callback_id, "No more jobs.")
#                 return

#             session["jobs"].extend(new_jobs)
#             session["page"] = next_page
#             session["index"] += 1

#     elif action == "prev":
#         if session["index"] > 0:
#             session["index"] -= 1
#         else:
#             await answer_callback(callback_id, "This is the first job.")
#             return

#     card, keyboard = build_card(chat_id)
#     await edit_message(chat_id, message_id, card, keyboard)
#     await answer_callback(callback_id)


# def build_card(chat_id):
#     session = user_sessions[chat_id]
#     jobs = session["jobs"]
#     index = session["index"]
#     job = jobs[index]

#     title = job.get("title", "Untitled")
#     company = job.get("company", "")
#     location = job.get("location", "")
#     url = job.get("url", "")
#     description = (job.get("description") or "").strip()

#     if len(description) > DESC_LIMIT:
#         description = description[:DESC_LIMIT].rsplit(" ", 1)[0] + "…"

#     lines = [f"*{title}*"]
#     if company:
#         lines.append(f"🏢 {company}")
#     if location:
#         lines.append(f"📍 {location}")
#     if description:
#         lines.append(f"\n{description}")
#     if url:
#         lines.append(f"\n🔗 {url}")
#     lines.append(f"\n({index + 1} of {len(jobs)}+)")

#     text = "\n".join(lines)

#     buttons = []
#     if index > 0:
#         buttons.append({"text": "◀ Prev", "callback_data": "prev"})
#     buttons.append({"text": "Next ▶", "callback_data": "next"})

#     keyboard = {"inline_keyboard": [buttons]}
#     return text, keyboard


# async def send_message(chat_id, text, keyboard=None):
#     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
#     payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
#     if keyboard:
#         payload["reply_markup"] = keyboard
#     requests.post(url, json=payload)


# async def edit_message(chat_id, message_id, text, keyboard=None):
#     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
#     payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
#     if keyboard:
#         payload["reply_markup"] = keyboard
#     requests.post(url, json=payload)


# async def answer_callback(callback_id, text=None):
#     url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
#     payload = {"callback_query_id": callback_id}
#     if text:
#         payload["text"] = text
#     requests.post(url, json=payload)




# import asyncio
# from mcp.client import Client

# async def main():
#     client = Client("server.py")

#     tools = await client.list_tools()
#     print("Tools:", tools)

#     result = await client.call_tool(
#         "search_jobs",
#         {"query": "AI engineer"}
#     )

#     print("Result:", result)

# asyncio.run(main())