# app/routes/user_routes.py
from fastapi import APIRouter
from utils import Response, UserQuery
from controller.apis import get_jobs, telegram_webhook
from fastapi import Request

router = APIRouter()

@router.get("/healthz", response_model=Response)
def create():
    return {"status":200, "message":"Server is running"}

@router.get("/jobs")
async def fetch_jobs(search, page=1, limit = 10, distance=0.9):
    # page=1, pagesize = 10, distance=0.4
    return await get_jobs(search, page, limit, distance)
@router.post("/jobs")
async def fetch_telegram_jobs(request: Request):
    # page=1, pagesize = 10, distance=0.4
    return await  telegram_webhook(request)