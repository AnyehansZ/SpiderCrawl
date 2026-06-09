import requests
from app.schema import ExtensionSuccess, ExtensionError

def crawl(url: str) -> dict:
    """
    Extension must implement crawl(url) function.
    Returns either ExtensionSuccess or ExtensionError format.
    """
    try:
        # Placeholder: actual parsing logic goes here
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Mock data structure
        data = {
            "title": "novel",
            "author": "Author Name",
            "chapters": [
                {
                    "chapter_num": 1,
                    "title": "Chapter 1",
                    "content": "Chapter content here..."
                }
            ],
            "cover_url": "https://example.com/cover.jpg",
            "description": "Novel description",
            "total_chapters": 100
        }
        
        return {
            "success": True,
            "data": data
        }
    
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "code": "REQUEST_FAILED"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "code": "PARSE_ERROR"
        }