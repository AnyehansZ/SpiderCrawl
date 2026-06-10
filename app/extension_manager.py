import requests
import json
import zipfile
from pathlib import Path
from app.config import EXTENSION_REGISTRY_URL, EXTENSIONS_DIR

class ExtensionManager:
    def __init__(self):
        self.registry_cache_path = EXTENSIONS_DIR / "registry_cache.json"
        self.local_registry = self.load_local_registry()
    
    def load_local_registry(self) -> dict:
        """Load cached registry from disk"""
        if self.registry_cache_path.exists():
            with open(self.registry_cache_path) as f:
                return json.load(f)
        return {"extensions": []}
    
    def fetch_remote_registry(self) -> dict:
        """Download latest registry from GitHub"""
        try:
            response = requests.get(EXTENSION_REGISTRY_URL, timeout=10)
            response.raise_for_status()
            registry = response.json()
            
            # Cache it locally
            with open(self.registry_cache_path, 'w') as f:
                json.dump(registry, f, indent=2)
            
            return registry
        except Exception as e:
            print(f"Failed to fetch registry: {e}")
            return self.local_registry
    
    def get_local_version(self, ext_name: str) -> str:
        """Get installed version of extension"""
        config_path = EXTENSIONS_DIR / ext_name / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f).get("version", "0.0.0")
        return None
    
    def download_extension(self, url: str, ext_name: str) -> bool:
        """Download extension files from folder URL"""
        try:
            files = ['parser.py', 'config.json', 'requirements.txt']
            ext_dir = EXTENSIONS_DIR / ext_name
            ext_dir.mkdir(exist_ok=True)
        
            for file in files:
                file_url = f"{url}{file}"
                response = requests.get(file_url, timeout=10)
                response.raise_for_status()
            
                with open(ext_dir / file, 'w') as f:
                    f.write(response.text)
        
            print(f"✓ {ext_name} installed")
            return True
    
        except Exception as e:
            print(f"✗ Failed to install {ext_name}: {e}")
            return False
    
    def check_updates(self) -> dict:
        """Compare local vs remote versions"""
        remote = self.fetch_remote_registry()
        updates = {}
        
        for ext in remote.get("extensions", []):
            name = ext["name"]
            remote_version = ext["version"]
            local_version = self.get_local_version(name)
            
            if local_version != remote_version:
                updates[name] = {
                    "local": local_version,
                    "remote": remote_version,
                    "download_url": ext["download_url"]
                }
        
        return updates
    
    def install_updates(self, updates: dict) -> dict:
        """Install available updates"""
        results = {}
        for ext_name, info in updates.items():
            success = self.download_extension(info["download_url"], ext_name)
            results[ext_name] = "installed" if success else "failed"
        return results