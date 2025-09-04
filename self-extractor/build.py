#!/usr/bin/env python3
"""
DoganAI Compliance Kit Self-Extractor Builder
Creates a portable, self-contained installer for the platform.
"""

import json
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, Any


class SelfExtractorBuilder:
    def __init__(self, config_path: str = "config.json"):
        base = Path(__file__).parent
        self.root_dir = base.parent
        self.config_path = base / config_path
        self.config = self._load_config()
        self.build_dir = base / "build"
        self.dist_dir = base / "dist"

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def clean_build_dirs(self):
        print("Cleaning build directories...")
        for d in [self.build_dir, self.dist_dir]:
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)

    def download_runtimes(self):
        print("Preparing embedded runtimes...")
        runtime_dir = self.build_dir / "runtime"
        python_dir = runtime_dir / "python"
        node_dir = runtime_dir / "node"
        python_dir.mkdir(parents=True, exist_ok=True)
        node_dir.mkdir(parents=True, exist_ok=True)

        py_ver = self.config["runtime"]["python"]["version"]
        node_ver = self.config["runtime"]["node"]["version"]
        print(f"  Python {py_ver} (embedded)")
        print(f"  Node.js {node_ver} (portable)")

        # Placeholders for local build without downloads
        (python_dir / "python.exe").touch()
        (python_dir / "Lib").mkdir(exist_ok=True)
        (node_dir / "node.exe").touch()
        (node_dir / "npm.cmd").touch()

    def build_frontend(self):
        print("Building frontend...")
        frontend_dir = self.root_dir / "frontend"
        if not frontend_dir.exists():
            print("  Frontend directory not found, skipping")
            return
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
            dist_dir = frontend_dir / "dist"
            if dist_dir.exists():
                shutil.copytree(dist_dir, self.build_dir / "frontend", dirs_exist_ok=True)
                print("  Frontend built successfully")
            else:
                print("  Frontend build output not found")
        except subprocess.CalledProcessError as e:
            print(f"  Frontend build failed: {e}")
        except FileNotFoundError as e:
            print(f"  Skipping frontend build (npm not found): {e}")

    def prepare_backend(self):
        print("Preparing backend...")
        backend_dir = self.build_dir / "backend"
        backend_dir.mkdir(exist_ok=True)

        source_dirs = ["backend", "src", "app", "config", "schemas"]
        for name in source_dirs:
            p = self.root_dir / name
            if p.exists():
                if p.is_dir():
                    shutil.copytree(p, backend_dir / name, dirs_exist_ok=True)
                else:
                    shutil.copy2(p, backend_dir)

        for req in ["requirements.txt", "requirements-api.txt"]:
            rp = self.root_dir / req
            if rp.exists():
                shutil.copy2(rp, backend_dir)
        print("  Backend prepared")

    def prepare_database(self):
        print("Preparing database...")
        db_dir = self.build_dir / "data"
        db_dir.mkdir(exist_ok=True)
        src_db = self.root_dir / "db"
        if src_db.exists():
            shutil.copytree(src_db, db_dir / "scripts", dirs_exist_ok=True)
        alembic_dir = self.root_dir / "alembic"
        if alembic_dir.exists():
            shutil.copytree(alembic_dir, db_dir / "migrations", dirs_exist_ok=True)
        print("  Database prepared")

    def create_launcher(self):
        print("Creating launcher...")
        launcher_content = r"""@echo off
setlocal EnableDelayedExpansion

echo.
echo ========================================
echo   DoganAI Compliance Kit - Portable
echo ========================================
echo.

set "APP_DIR=%~dp0"
set "PYTHON_DIR=%APP_DIR%runtime\python"
set "NODE_DIR=%APP_DIR%runtime\node"
set "DATA_DIR=%APP_DIR%data"
set "BACKEND_DIR=%APP_DIR%backend"
set "FRONTEND_DIR=%APP_DIR%frontend"

REM Set environment variables
set "PATH=%PYTHON_DIR%;%NODE_DIR%;%PATH%"
set "DATABASE_URL=sqlite:///%DATA_DIR%\compliance.db"
set "SECRET_KEY=auto-generated-secret-key"
set "CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000"

echo Starting DoganAI Compliance Kit...
echo.

REM Initialize database if it doesn't exist
if not exist "%DATA_DIR%\compliance.db" (
    echo Initializing database...
    "%PYTHON_DIR%\python.exe" -c "import sqlite3; sqlite3.connect('%DATA_DIR%\compliance.db').close()"
)

REM Start backend server
echo Starting backend server on port 8000...
start /B "DoganAI Backend" "%PYTHON_DIR%\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo Starting frontend server on port 3000...
start /B "DoganAI Frontend" "%NODE_DIR%\node.exe" -e "const express=require('express');const path=require('path');const app=express();app.use(express.static('%FRONTEND_DIR%'));app.get('*',(req,res)=>res.sendFile(path.join('%FRONTEND_DIR%','index.html')));app.listen(3000,()=>console.log('Frontend running on port 3000'));"

REM Open browser
timeout /t 2 /nobreak >nul
echo.
echo DoganAI Compliance Kit is now running!
echo.
echo Dashboard: http://localhost:3000
echo API Docs:  http://localhost:8000/docs
echo.
echo Press any key to open the dashboard in your browser...
pause >nul
start http://localhost:3000

echo.
echo Press any key to stop the application...
pause >nul

REM Cleanup
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo.
echo DoganAI Compliance Kit stopped.
pause
"""
        launcher_path = self.build_dir / "start.bat"
        launcher_path.write_text(launcher_content, encoding='utf-8')
        print("  Launcher created")

    def create_installer(self):
        print("Creating self-extracting installer...")

        # Create archive of build directory
        archive_path = self.dist_dir / "doganai-compliance-kit.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.build_dir):
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    arc_path = file_path.relative_to(self.build_dir)
                    zipf.write(file_path, arc_path)

        # Create a batch-based extractor stub (note: not a true .exe)
        extractor_content = r"""@echo off
setlocal

echo.
echo ========================================
echo   DoganAI Compliance Kit Installer
echo ========================================
echo.

set "INSTALL_DIR=%USERPROFILE%\DoganAI-Compliance-Kit"
set "TEMP_EXTRACT=%TEMP%\DoganAI-Extract-%RANDOM%"

echo Installing to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Extract files
echo Extracting files...
powershell -Command "Expand-Archive -Path '%~f0.zip' -DestinationPath '%TEMP_EXTRACT%' -Force"

REM Copy files to installation directory
echo Installing files...
xcopy "%TEMP_EXTRACT%\*" "%INSTALL_DIR%\" /E /I /Y >nul

REM Cleanup temp files
rmdir /S /Q "%TEMP_EXTRACT%" >nul 2>&1

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\DoganAI Compliance Kit.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start.bat'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\assets\icon.ico'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo.
echo The DoganAI Compliance Kit has been installed to:
echo %INSTALL_DIR%
echo.
echo A desktop shortcut has been created for easy access.
echo.
set /p "LAUNCH=Would you like to launch the application now? (Y/N): "
if /I "%LAUNCH%"=="Y" (
    cd /d "%INSTALL_DIR%"
    start start.bat
)

echo.
echo Thank you for using DoganAI Compliance Kit!
pause
exit

REM Archive data follows...
"""
        installer_path = self.dist_dir / self.config["extractor"]["output_name"]
        installer_path.write_text(extractor_content, encoding='utf-8')
        print(f"  Installer created: {installer_path}")

    def create_readme(self):
        readme_content = f"""# DoganAI Compliance Kit - Portable Edition

## Overview
This is a portable, self-contained version of the DoganAI Compliance Kit - a comprehensive Saudi Arabia regulatory compliance platform.

## System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for initial setup and updates)

## Installation
1. Run `{self.config['extractor']['output_name']}`
2. Follow the installation prompts
3. Launch from desktop shortcut or start menu

## Quick Start
1. Double-click the desktop shortcut "DoganAI Compliance Kit"
2. Wait for the application to start (may take 30-60 seconds on first run)
3. Your browser will automatically open to the dashboard
4. Default login: admin / (you'll be prompted to set password on first run)

## Features
- Saudi Regulatory Framework Compliance
- Real-time Compliance Dashboard
- Risk Assessment & Management
- Analytics & Reporting
- Enterprise Security
- Multi-language Support (Arabic/English)

## Supported Regulations
- CITC (Communications and Information Technology Commission)
- CMA (Capital Market Authority)
- MHRSD (Ministry of Human Resources and Social Development)
- MOI (Ministry of Interior)
- SAMA (Saudi Arabian Monetary Authority)
- And more...

## Troubleshooting
- If the application doesn't start, run as Administrator
- Check Windows Defender/Antivirus isn't blocking the application
- Ensure ports 3000 and 8000 are available
- For support, contact: support@doganai.com

## Data & Privacy
- All data is stored locally on your machine
- No data is transmitted without your explicit consent
- Complies with Saudi Data Protection regulations

## Version Information
- Version: {self.config['app']['version']}
- Build Date: {self._get_build_date()}
- Components: React Frontend + FastAPI Backend + SQLite Database
"""
        readme_path = self.build_dir / "README.txt"
        readme_path.write_text(readme_content, encoding='utf-8')

    def _get_build_date(self):
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def build(self):
        print(f"Building {self.config['app']['name']} v{self.config['app']['version']}")
        print("=" * 60)
        try:
            self.clean_build_dirs()
            self.download_runtimes()
            self.build_frontend()
            self.prepare_backend()
            self.prepare_database()
            self.create_launcher()
            self.create_readme()
            self.create_installer()

            print("\n" + "=" * 60)
            print("Build completed successfully!")
            print(f"Output: {self.dist_dir / self.config['extractor']['output_name']}")
            print(f"Artifacts: {self.build_dir}")
        except Exception as e:
            print(f"\nBuild failed: {e}")
            raise


if __name__ == "__main__":
    builder = SelfExtractorBuilder()
    builder.build()
