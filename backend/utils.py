from pydantic import BaseModel
from typing import Optional

class Response(BaseModel):
    status: int
    message: str
    
class UserQuery(BaseModel):
    query: str
    location: Optional[str] = None,
    salary: Optional[int] = None,
    remote: Optional[bool] = None