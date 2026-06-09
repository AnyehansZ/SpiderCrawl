from dataclasses import dataclass
from datetime import datetime

@dataclass
class Novel:
    id: int
    title: str
    author: str
    source_url: str
    source_site: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Chapter:
    id: int
    novel_id: int
    chapter_num: int
    title: str
    content: str
    crawled_at: datetime

@dataclass
class Metadata:
    id: int
    novel_id: int
    cover_url: str
    description: str
    status: str  # 'crawling', 'complete', 'paused'
    total_chapters: int

@dataclass
class ExtensionRegistry:
    name: str
    version: str
    enabled: bool
    last_updated: datetime