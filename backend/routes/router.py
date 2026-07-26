# app/routes/user_routes.py
from fastapi import APIRouter
from utils import Response, UserQuery
from controller.apis import get_jobs

router = APIRouter()

@router.get("/healthz", response_model=Response)
def create():
    return {"status":200, "message":"Server is running"}

@router.get("/jobs")
def fetch_jobs(search, page=1, limit = 10, distance=0.9):
    # page=1, pagesize = 10, distance=0.4
    return get_jobs(search, page, limit, distance)