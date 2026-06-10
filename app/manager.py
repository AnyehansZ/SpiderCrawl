from typing import Optional, Dict
from urllib.parse import urlparse
from app.database.db import init_db
from app.extension_manager import ExtensionManager
from app.config import EXTENSIONS_DIR
import json
import importlib


class Manager:
    def __init__(self):
        init_db()
        self.extensions = {}
        self.ext_manager = ExtensionManager()
        self.load_extension_registry()
    
    def load_extension_registry(self):
        """Load available extensions from extensions directory"""
        for ext_dir in EXTENSIONS_DIR.iterdir():
            if ext_dir.is_dir() and not ext_dir.name.startswith('_'):
                config_path = ext_dir / "config.json"
                if config_path.exists():
                    with open(config_path) as f:
                        config = json.load(f)
                    self.extensions[ext_dir.name] = {
                        'path': ext_dir,
                        'version': config.get('version'),
                        'name': ext_dir.name
                    }
    
    def identify_site(self, url: str) -> Optional[str]:
        """Extract domain from URL and match to extension"""
        domain = urlparse(url).netloc.replace('www.', '').split('.')[0]
        return domain if domain in self.extensions else None
    
    def get_extension(self, site_name: str):
        """Load extension module dynamically"""
        if site_name not in self.extensions:
            return None
        
        ext_path = self.extensions[site_name]['path']
        # Dynamic import of extension's parser module
        spec = importlib.util.spec_from_file_location(
            f"{site_name}.parser",
            ext_path / "parser.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def crawl(self, url: str) -> Dict:
        """Main crawl method: identify site -> load extension -> execute"""
        site_name = self.identify_site(url)
        
        if not site_name:
            return {"success": False, "error": "Site not supported", "code": "SITE_NOT_FOUND"}
        if site_name not in self.extensions:
            print(f"Extension '{site_name}' not found locally. Checking registry...")
        
            remote = self.ext_manager.fetch_remote_registry()
            ext_info = next(
            (e for e in remote.get("extensions", []) if e["name"] == site_name),
            None
            )
            if ext_info:
                print(f"Found in registry. Installing...")
                if self.ext_manager.download_extension(ext_info["download_url"], site_name):
                    self.load_extension_registry()  # Reload
                else:
                    return {"success": False, "error": "Failed to install extension", "code": "EXT_INSTALL_FAILED"}
            else:
                return {"success": False, "error": "Extension not in registry", "code": "EXT_NOT_FOUND"}
    
        extension = self.get_extension(site_name)
        if not extension:
            return {"success": False, "error": "Extension failed to load", "code": "EXT_LOAD_FAILED"}
        
        try:
            # Extension must have crawl() function
            result = extension.crawl(url)
            return result
        except Exception as e:
            return {"success": False, "error": str(e), "code": "CRAWL_ERROR"}
    
    def search(self, title: str) -> Optional[Dict]:
        """Search for novel by title across supported sites"""
        # Will implement after extensions are ready
        pass