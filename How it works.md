# SpiderCrawl — Workflow & Architecture Flow

## App Initialization

```
main.py starts
    ↓
load_dotenv() → reads .env file
    ↓
init_db() → creates/connects to database.db
    ↓
Manager() instantiated
    ├→ load_extension_registry() 
    │   └→ scans extensions/ folder
    │       └→ reads config.json from each extension
    │           └→ stores in self.extensions dict
    │
    └→ ExtensionManager() instantiated
        ├→ load_local_registry() 
        │   └→ reads registry_cache.json (if exists)
        │
        └→ fetch_remote_registry() [optional, user triggered]
            └→ downloads registry.json from GitHub
                └→ caches it locally as registry_cache.json

    ↓
Display menu to user
```

---

## Workflow 1: Crawl by URL

```
User selects "1. Crawl by URL"
    ↓
User inputs URL (e.g., https://example-novel-site.com/novel/123)
    ↓
manager.crawl(url) called
    ├→ identify_site(url)
    │   ├→ Extract domain from URL
    │   └→ Check if site_name exists in self.extensions
    │       └→ Return site_name or None
    │
    ├→ If site not found
    │   └→ Return {"success": False, "error": "Site not supported"}
    │       └→ [STOP]
    │
    ├→ If site found but extension missing locally
    │   ├→ ext_manager.fetch_remote_registry()
    │   ├→ Check if site in remote registry
    │   ├→ ext_manager.download_extension(url, site_name)
    │   │   ├→ fetch_html(download_url) × 3 files
    │   │   ├→ Write parser.py, config.json, requirements.txt
    │   │   └→ Return True/False
    │   └→ If download failed: return error
    │
    ├→ get_extension(site_name)
    │   └→ Dynamically import parser.py module
    │       └→ Return module or None
    │
    ├→ extension.crawl(url) executed
    │   ├→ fetch_html(url) [app/utils/helpers.py]
    │   │   ├→ requests.get(url, timeout=10)
    │   │   ├→ Retry up to MAX_RETRIES times
    │   │   ├→ Sleep RATE_LIMIT_DELAY between requests
    │   │   └→ Return HTML string
    │   │
    │   ├→ BeautifulSoup(html, "lxml") → parse HTML
    │   │
    │   ├→ Extract metadata (title, author, description, cover_url)
    │   │
    │   ├→ Extract chapter links
    │   │
    │   ├→ For each chapter link:
    │   │   ├→ fetch_html(chapter_url)
    │   │   ├→ Parse title & content
    │   │   └→ Add to chapters list
    │   │
    │   └→ Return {"success": True, "data": {...}}
    │
    ├→ manager.store_crawl_result(result, url)
    │   ├→ Extract data from result
    │   │
    │   ├→ INSERT into novels table
    │   │   ├→ title, author, source_url, source_site
    │   │   └→ Get novel_id from lastrowid
    │   │
    │   ├→ INSERT into metadata table
    │   │   ├→ cover_url, description, total_chapters, status='crawled'
    │   │   └→ Link to novel_id
    │   │
    │   ├→ INSERT into chapters table (loop for each)
    │   │   ├→ chapter_num, title, content
    │   │   └→ Link to novel_id
    │   │
    │   └→ COMMIT transaction
    │
    └→ Print success message

[RETURN TO MENU]
```

---

## Workflow 2: Check & Install Extension Updates

```
User selects "2. Check extension updates"
    ↓
ext_manager.fetch_remote_registry()
    ├→ requests.get(EXTENSION_REGISTRY_URL) [GitHub raw URL]
    ├→ Parse JSON
    └→ Cache locally as registry_cache.json
    
    ↓
ext_manager.check_updates()
    ├→ For each extension in remote registry:
    │   ├→ Get remote_version from registry
    │   ├→ Get local_version from config.json
    │   └→ If different: add to updates dict
    │
    └→ Return updates dict
    
    ↓
If updates found:
    ├→ Display: "Updates available: {extension_names}"
    │
    ├→ User selects "y" to install
    │   │
    │   ├→ ext_manager.install_updates(updates)
    │   │   ├→ For each extension to update:
    │   │   │   ├→ fetch download_url from updates dict
    │   │   │   ├→ download_extension(url, ext_name)
    │   │   │   │   ├→ GET each file from GitHub
    │   │   │   │   ├→ Overwrite existing files
    │   │   │   │   └→ Return True/False
    │   │   │   │
    │   │   │   └→ Update version in local config.json
    │   │   │
    │   │   └→ Return results dict
    │   │
    │   └→ manager.load_extension_registry() [reload]
    │       └→ Refresh self.extensions dict
    │
    └→ Else: print "All extensions up to date"

[RETURN TO MENU]
```

---

## Workflow 3: Build EPUB

```
User selects "3. Build EPUB"
    ↓
Query database:
    ├→ SELECT id, title, author FROM novels
    ├→ Display list to user
    └→ User selects novel by number
    
    ↓
EPUBBuilder(novel_id) instantiated
    ├→ get_novel_data()
    │   ├→ SELECT * FROM novels WHERE id = novel_id
    │   └→ LEFT JOIN metadata
    │
    └→ get_chapters()
        ├→ SELECT * FROM chapters WHERE novel_id = novel_id
        └→ ORDER BY chapter_num ASC
    
    ↓
builder.build(output_name=None)
    ├→ Validate novel data exists
    │
    ├→ Create ZIP file at EPUB_OUTPUT_DIR/novel_title.epub
    │   ├→ Write "mimetype" (uncompressed)
    │   ├→ Generate & write "META-INF/container.xml"
    │   ├→ Generate & write "OEBPS/content.opf" (metadata + manifest)
    │   ├→ Generate & write "OEBPS/toc.ncx" (table of contents)
    │   │
    │   └→ For each chapter:
    │       ├→ generate_chapter_xhtml(chapter)
    │       │   └→ Create HTML structure with chapter title & content
    │       │
    │       └→ Write to "OEBPS/chapters/ch_001.xhtml"
    │
    ├→ Close ZIP file
    │
    └→ Print success: "EPUB created at: {path}"

[RETURN TO MENU]
```

---

## Database Schema & Flow

```
novels table
├── id (PK)
├── title
├── author
├── source_url (UNIQUE)
├── source_site
├── created_at
└── updated_at

    ↕ (1:N relationship)

chapters table
├── id (PK)
├── novel_id (FK → novels.id)
├── chapter_num
├── title
├── content
└── crawled_at

    ↕ (1:1 relationship)

metadata table
├── id (PK)
├── novel_id (FK → novels.id, UNIQUE)
├── cover_url
├── description
├── status (idle/crawling/complete)
└── total_chapters

extension_registry table
├── name (PK)
├── version
├── enabled
└── last_updated
```

---

## File System Structure

### Development (CLI Mode)
```
novel-crawler/
├── database.db               ← Created by init_db()
├── extensions/
│   └── example_site/         ← Downloaded by download_extension()
│       ├── parser.py
│       ├── config.json
│       └── requirements.txt
├── output/                   ← Created by build()
│   └── Novel_Title.epub
├── logs/
└── registry_cache.json       ← Cached by fetch_remote_registry()
```

### Production (Windows EXE Mode)
```
Downloads/spidercrawl/       ← User-friendly location
├── database.db
├── extensions/
├── output/                   ← User sees generated EPUBs here
├── logs/
└── registry_cache.json
```

---

## Trigger Chain Summary

| Event                      | Trigger             | Action                                                                     |
| -------------------------- | ------------------- | -------------------------------------------------------------------------- |
| App Start                  | `python main.py`    | init_db(), load extensions, show menu                                      |
| Crawl                      | User selects "1"    | identify_site() → auto-install if missing → crawl() → store_crawl_result() |
| Check Updates              | User selects "2"    | fetch_remote_registry() → check_updates() → compare versions               |
| Install Update             | User selects "y"    | download_extension() → extract files → reload extensions                   |
| Build EPUB                 | User selects "3"    | query novels → select → EPUBBuilder() → generate files → zip               |
| Missing Extension on Crawl | Extension not local | download_extension() → install → resume crawl                              |