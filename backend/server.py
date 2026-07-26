from fastapi import FastAPI
from routes.router import router
app = FastAPI()

app.include_router(router, prefix="/api", tags=["Jobs"])

# GET /jobs/search?q=python remote 2 years
