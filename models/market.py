from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str

class ProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    category: str
    created_at: datetime
    seller: str