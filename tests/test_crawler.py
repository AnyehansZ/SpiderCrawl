from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.manager import Manager

manager = Manager()
print(f"Extensions loaded: {list(manager.extensions.keys())}")

# Test crawl
result = manager.crawl("https://example-site.com")
print(f"\nCrawl result: {result}")