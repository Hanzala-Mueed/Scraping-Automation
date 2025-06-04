from pydantic import BaseModel
from typing import Dict, Optional

class SoftwareCreate(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    subcategory: Optional[str] = None
    category: Optional[str] = None
    downloads: Optional[str] = None
    size: Optional[Dict[str, str]] = None
    download_link: Optional[str] = None
    password: Optional[str] = None

    class Config:
        orm_mode = True




class CategoryCreate(BaseModel):
    title: str
    url: str
    primary_category: str
    sub_category: str
    child_category: str | None = None

class Category(CategoryCreate):
    id: int

    class Config:
        orm_mode = True


