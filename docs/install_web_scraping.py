#!/usr/bin/env python3
"""
Auto-install Web Scraping Dependencies
"""

import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package):
    """Check if a package is installed"""
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False

def main():
    """Install required packages for web scraping"""
    
    print("🔧 Installing Web Scraping Dependencies")
    print("=" * 40)
    
    # Required packages for web scraping
    packages = {
        'requests': 'HTTP library for API calls',
        'beautifulsoup4': 'HTML parsing for web scraping',
        'aiohttp': 'Async HTTP client',
        'lxml': 'XML/HTML parser (optional but faster)'
    }
    
    installed_count = 0
    
    for package, description in packages.items():
        print(f"\n📦 {package}: {description}")
        
        # Check if already installed
        check_name = package
        if package == 'beautifulsoup4':
            check_name = 'bs4'
        
        if check_package(check_name):
            print(f"✅ Already installed")
            installed_count += 1
        else:
            print(f"⬇️ Installing...")
            if install_package(package):
                print(f"✅ Successfully installed")
                installed_count += 1
            else:
                print(f"❌ Installation failed")
    
    print(f"\n📊 Installation Summary:")
    print(f"Packages: {installed_count}/{len(packages)} installed")
    
    if installed_count == len(packages):
        print(f"\n🎉 All dependencies installed!")
        print(f"You can now run:")
        print(f"   • python website_auto_connector.py")
        print(f"   • python regulatory_web_scraper.py")
    else:
        print(f"\n⚠️ Some packages failed to install")
        print(f"Try manually: pip install requests beautifulsoup4 aiohttp")

if __name__ == "__main__":
    main()
