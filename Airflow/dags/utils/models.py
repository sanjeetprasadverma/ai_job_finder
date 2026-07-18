from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Job(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    skills: List[str] = []
    source: str
    apply_url: Optional[str] = None
    posted_date: Optional[datetime] = None
    # load_time: datetime = datetime.now()