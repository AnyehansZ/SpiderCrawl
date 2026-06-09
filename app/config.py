from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_PATH = BASE_DIR / "database.db"
EXTENSIONS_DIR = BASE_DIR / "extensions"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
EXTENSIONS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Extension settings
EXTENSION_REGISTRY_URL = os.getenv("EXTENSION_REGISTRY_URL", "")
EXTENSION_UPDATE_CHECK = os.getenv("EXTENSION_UPDATE_CHECK", "true").lower() == "true"

# Crawling settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))  # seconds between requests
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# EPUB settings
EPUB_OUTPUT_DIR = BASE_DIR / "output"
EPUB_OUTPUT_DIR.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")