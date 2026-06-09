from pydantic import BaseModel , RootModel
from typing import Optional, Any, Union
from datetime import datetime

# Extension response contract
class ExtensionSuccess(BaseModel):
    success: bool = True
    data: dict

class ExtensionError(BaseModel):
    success: bool = False
    error: str
    code: str

class ExtensionResponse(RootModel):
    root: Union[ExtensionSuccess, ExtensionError]

# Data models
class NovelCreate(BaseModel):
    title: str
    author: Optional[str] = None
    source_url: str
    source_site: str

class NovelRead(NovelCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class ChapterCreate(BaseModel):
    novel_id: int
    chapter_num: int
    title: str
    content: str

class ChapterRead(ChapterCreate):
    id: int
    crawled_at: datetime

class MetadataCreate(BaseModel):
    novel_id: int
    cover_url: Optional[str] = None
    description: Optional[str] = None
    status: str = "idle"
    total_chapters: int = 0

class ExtensionInfo(BaseModel):
    name: str
    version: str
    enabled: bool