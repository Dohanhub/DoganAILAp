# DoganAI Compliance Kit - Self-Extractor

## Overview
This directory contains the self-extractor system for creating a portable, standalone version of the DoganAI Compliance Kit. The self-extractor packages the entire application with embedded runtimes into a single executable installer.

## Features
- **Portable Installation**: No external dependencies required
- **Embedded Runtimes**: Includes Python 3.11 and Node.js 20
- **SQLite Database**: Lightweight, file-based database
- **Security Compliant**: Follows Saudi regulatory security standards
- **One-Click Setup**: Simple installation and launch process

## Build Process

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.11+ (for building)
- Node.js 20+ (for building)
- Internet connection (for downloading runtimes)

### Quick Build
```bash
# Run the automated build script
build.bat
```

### Manual Build
```bash
# Install dependencies and build
python build.py

# Or use the package manager directly
python package_manager.py
```

## File Structure
```
self-extractor/
├── config.json              # Build configuration
├── build.py                 # Main build script
├── package_manager.py       # Runtime and dependency manager
├── portable_server.py       # Portable server manager
├── installer.nsi           # NSIS installer script
├── build.bat               # Windows build script
├── build/                  # Build artifacts (generated)
├── dist/                   # Final installer (generated)
└── cache/                  # Downloaded runtimes (generated)
```

## Configuration
Edit `config.json` to customize:
- Application metadata
- Runtime versions
- Component ports
- Security settings
- Installer options

## Output
The build process creates:
1. **Portable Version**: `build/` directory with complete application
2. **Installer**: `dist/DoganAI-Compliance-Kit-Portable.exe`

## Testing
After building, test the portable version:
```bash
cd build
start.bat
```

## Security Features
- Environment-based configuration
- Secure default settings
- Local SQLite database
- No hardcoded secrets
- CORS protection
- Self-signed SSL certificates

## Supported Regulations
The portable version includes compliance frameworks for:
- CITC (Communications and Information Technology Commission)
- CMA (Capital Market Authority)
- MHRSD (Ministry of Human Resources and Social Development)
- MOI (Ministry of Interior)
- SAMA (Saudi Arabian Monetary Authority)

## Deployment
1. Build the installer using `build.bat`
2. Distribute `DoganAI-Compliance-Kit-Portable.exe`
3. Users run the installer and launch from desktop shortcut
4. Application runs locally on ports 3000 (frontend) and 8000 (backend)

## Troubleshooting
- Ensure Windows Defender allows the application
- Check that ports 3000 and 8000 are available
- Run as Administrator if installation fails
- Check logs in the application data directory

## Support
For technical support or questions:
- Documentation: See `docs/` directory
- Issues: Contact DoganAI support team
- Updates: Check for new releases periodically
