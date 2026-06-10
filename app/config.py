import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Detect if running as exe or CLI
if getattr(sys, 'frozen', False):
    # Running as .exe - use Downloads folder
    BASE_DIR = Path.home() / "Downloads" / "spidercrawl"
else:
    # Running as CLI (development)
    BASE_DIR = Path(__file__).parent.parent

# Paths
DATABASE_PATH = BASE_DIR / "database.db"
EXTENSIONS_DIR = BASE_DIR / "extensions"
LOGS_DIR = BASE_DIR / "logs"
EPUB_OUTPUT_DIR = BASE_DIR / "output"

# Ensure directories exist
for directory in [BASE_DIR, EXTENSIONS_DIR, LOGS_DIR, EPUB_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Extension settings
EXTENSION_REGISTRY_URL = "https://raw.githubusercontent.com/AnyehansZ/SpiderCrawl-extensions/main/registry.json"
EXTENSION_UPDATE_CHECK = os.getenv("EXTENSION_UPDATE_CHECK", "true").lower() == "true"

# Crawling settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")