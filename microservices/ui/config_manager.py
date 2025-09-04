#!/usr/bin/env python3
"""
Configuration Manager for DoganAI Compliance Kit
Handles multi-language support and hot-reload configuration
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigManager:
    """Manages configuration files with hot-reload support"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        self.last_modified = {}
        self.observer = None
        self.watchdog_enabled = False
        
        # Load initial configurations
        self._load_all_configs()
        
        # Start file watching if watchdog is available
        self._start_file_watching()
    
    def _load_all_configs(self):
        """Load all configuration files"""
        config_files = [
            "dashboard_config.json",
            "ui_config.json",
            "language_config.json"
        ]
        
        for config_file in config_files:
            self._load_config(config_file)
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load a specific configuration file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            print(f"⚠️ Configuration file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.config_cache[filename] = config_data
            self.last_modified[filename] = config_path.stat().st_mtime
            
            print(f"✅ Loaded configuration: {filename}")
            return config_data
            
        except Exception as e:
            print(f"❌ Error loading configuration {filename}: {e}")
            return {}
    
    def get_config(self, filename: str, key: Optional[str] = None) -> Any:
        """Get configuration value"""
        if filename not in self.config_cache:
            self._load_config(filename)
        
        config = self.config_cache.get(filename, {})
        
        if key is None:
            return config
        
        # Support nested keys like "dashboard.metrics.total_tests"
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def get_language_text(self, key: str, language: str = "en") -> str:
        """Get localized text for a given key and language"""
        # Try to get from dashboard config first
        dashboard_config = self.get_config("dashboard_config.json")
        
        # Navigate through nested structure to find the text
        keys = key.split('.')
        value = dashboard_config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return key  # Return key if not found
        
        # If value is a dict with language keys
        if isinstance(value, dict) and language in value:
            return value[language]
        
        # If value is a string, return as is
        if isinstance(value, str):
            return value
        
        return key
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get theme colors from configuration"""
        dashboard_config = self.get_config("dashboard_config.json")
        return dashboard_config.get("theme", {})
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        dashboard_config = self.get_config("dashboard_config.json")
        return dashboard_config.get("languages", ["en"])
    
    def is_rtl_language(self, language: str) -> bool:
        """Check if language is RTL (right-to-left)"""
        dashboard_config = self.get_config("dashboard_config.json")
        rtl_languages = dashboard_config.get("rtl_languages", [])
        return language in rtl_languages
    
    def _start_file_watching(self):
        """Start watching configuration files for changes"""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class ConfigFileHandler(FileSystemEventHandler):
                def __init__(self, config_manager):
                    self.config_manager = config_manager
                
                def on_modified(self, event):
                    if not event.is_directory and event.src_path.endswith('.json'):
                        filename = os.path.basename(event.src_path)
                        print(f"🔄 Configuration file changed: {filename}")
                        # Reload the changed configuration
                        self.config_manager._load_config(filename)
            
            self.observer = Observer()
            handler = ConfigFileHandler(self)
            self.observer.schedule(handler, str(self.config_dir), recursive=False)
            self.observer.start()
            self.watchdog_enabled = True
            print("✅ File watching enabled - configuration changes will auto-reload")
            
        except ImportError:
            print("⚠️ Watchdog not available - manual reload required for configuration changes")
            self.watchdog_enabled = False
    
    def stop_watching(self):
        """Stop file watching"""
        if self.observer and self.watchdog_enabled:
            self.observer.stop()
            self.observer.join()
            print("🛑 File watching stopped")
    
    def reload_all(self):
        """Manually reload all configurations"""
        print("🔄 Reloading all configurations...")
        self._load_all_configs()
        print("✅ All configurations reloaded")

# Global configuration manager instance
config_manager = ConfigManager()
