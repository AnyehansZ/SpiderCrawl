# SpiderCrawl — Extension Development Guide

## Overview
An extension is a directory that teaches the crawler how to extract novel data from a specific website.
You only need to provide the **profile/landing page URL** of a novel to start crawling.

---

## Required Structure
```
your_site_name/
├── parser.py          # Core crawling logic
├── config.json        # Extension metadata
└── requirements.txt   # Leave empty (dependencies handled by main app)
```

---

## config.json
```json
{
  "name": "your_site_name",
  "version": "1.0.0",
  "site_url": "https://example-novel-site.com",
  "author": "your_name",
  "description": "Short description of the site"
}
```

---

## Communication Contract
Every extension **must** implement one function:
```python
def crawl(url: str) -> dict
```

### On success return:
```python
{
  "success": True,
  "data": {
    "title": str,
    "author": str,
    "description": str,
    "cover_url": str,
    "total_chapters": int,
    "chapters": [
      {
        "chapter_num": int,
        "title": str,
        "content": str
      }
    ]
  }
}
```

### On failure return:
```python
{
  "success": False,
  "error": "Human readable description of what went wrong",
  "code": "ERROR_CODE"
}
```

### Error codes:
| Code | Meaning |
|------|---------|
| `REQUEST_FAILED` | HTTP request failed |
| `PARSE_ERROR` | HTML parsing failed |
| `NO_CHAPTERS` | No chapters found on page |
| `BLOCKED` | Site returned 403/captcha |
| `STRUCTURE_CHANGED` | Expected HTML elements missing |

---

## Shared Utilities
Do **not** use `requests` directly. Import the shared fetcher:

```python
from app.utils.helpers import fetch_html
from bs4 import BeautifulSoup
```

`fetch_html(url)` handles:
- Rate limiting between requests
- Retries on failure
- User-Agent headers

---

## parser.py Template
```python
from app.utils.helpers import fetch_html
from bs4 import BeautifulSoup

def get_novel_metadata(soup: BeautifulSoup) -> dict:
    """Extract metadata from profile/landing page"""
    return {
        "title": soup.select_one("SELECTOR").get_text(strip=True),
        "author": soup.select_one("SELECTOR").get_text(strip=True),
        "description": soup.select_one("SELECTOR").get_text(strip=True),
        "cover_url": soup.select_one("SELECTOR").get("src", ""),
        "chapter_links": [
            a.get("href")
            for a in soup.select("SELECTOR")
        ]
    }

def get_chapter_content(url: str, chapter_num: int) -> dict:
    """Extract content from a single chapter page"""
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    return {
        "chapter_num": chapter_num,
        "title": soup.select_one("SELECTOR").get_text(strip=True),
        "content": soup.select_one("SELECTOR").get_text(strip=True)
    }

def crawl(url: str) -> dict:
    try:
        # Step 1: Fetch profile page
        html = fetch_html(url)
        soup = BeautifulSoup(html, "lxml")

        # Step 2: Extract metadata + chapter links
        meta = get_novel_metadata(soup)

        if not meta["chapter_links"]:
            return {
                "success": False,
                "error": "No chapters found",
                "code": "NO_CHAPTERS"
            }

        # Step 3: Crawl each chapter
        chapters = []
        for i, link in enumerate(meta["chapter_links"], 1):
            chapter = get_chapter_content(link, i)
            chapters.append(chapter)

        return {
            "success": True,
            "data": {
                "title": meta["title"],
                "author": meta["author"],
                "description": meta["description"],
                "cover_url": meta["cover_url"],
                "total_chapters": len(chapters),
                "chapters": chapters
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": "PARSE_ERROR"
        }
```

---

## How to Build an Extension from HTML Samples
When building an extension, you need three HTML samples:
1. **Profile page** — landing page of the novel
2. **Chapter 1 page** — first chapter content
3. **Chapter 2 page** — second chapter content (to confirm consistency)

### Step 1: Identify metadata from profile page HTML
Look for:
- Novel title — usually `<h1>` or prominent heading
- Author name — near title or in metadata section
- Description/synopsis — usually in `<div>` or `<p>` block
- Cover image — `<img>` tag near title
- Chapter list — repeated `<a>` tags linking to chapters (look for patterns like `/chapter-1`, `/ch-001`)

### Step 2: Identify chapter content
Look for:
- Chapter title — `<h1>` or `<h2>` at top of content
- Chapter body — large `<div>` containing paragraphs

### Step 3: Replace SELECTOR placeholders
Use CSS selectors. Examples:
```python
soup.select_one("h1.novel-title")          # by class
soup.select_one("#chapter-content")         # by id
soup.select_one("div.content > p")          # nested
soup.select("ul.chapter-list a")            # list of links
```

### Step 4: Handle pagination
If chapter list spans multiple pages:
```python
next_page = soup.select_one("a.next-page")
while next_page:
    html = fetch_html(next_page.get("href"))
    soup = BeautifulSoup(html, "lxml")
    # collect more chapter links
    next_page = soup.select_one("a.next-page")
```

---

## Rules
- Never hardcode chapter URLs — always extract from profile page
- Always strip whitespace from text: `.get_text(strip=True)`
- Never import `requests` directly — use `fetch_html`
- Always return correct success/error format — nothing else
- `chapter_num` must be an integer starting from `1`
- `content` must be plain text, not HTML

---

## Testing Your Extension
Before submitting, verify your `crawl()` returns:
- `success: True`
- `data.chapters` is a non-empty list
- Each chapter has `chapter_num`, `title`, `content`
- No raw HTML in `content` field