# Dogan.com Domain Scraper - Usage Guide

## Overview
This comprehensive scraper will extract 100% of your dogan.com domain content, including all pages, images, CSS, JavaScript, and other resources.

## Features
- ✅ **Certificate Authentication** - Supports PFX certificates with PIN codes
- ✅ **Basic Authentication** - Username/password authentication
- ✅ **Recursive Scraping** - Follows all links within your domain
- ✅ **Resource Download** - Downloads all images, CSS, and JS files
- ✅ **Structured Data** - Extracts meta tags, headers, forms, and scripts
- ✅ **Comprehensive Reports** - Generates detailed JSON summaries and HTML index

## Usage Options

### 1. Basic Scraping (No Authentication)
```powershell
powershell -ExecutionPolicy Bypass -File "dogan-domain-scraper.ps1"
```

### 2. With Certificate Authentication
```powershell
powershell -ExecutionPolicy Bypass -File "dogan-domain-scraper.ps1" -CertificatePath "C:\path\to\your\certificate.pfx" -PinCode "your-pin-code"
```

### 3. With Basic Authentication
```powershell
powershell -ExecutionPolicy Bypass -File "dogan-domain-scraper.ps1" -Username "your-username" -Password "your-password"
```

### 4. With Both Certificate and Basic Auth
```powershell
powershell -ExecutionPolicy Bypass -File "dogan-domain-scraper.ps1" -CertificatePath "C:\path\to\your\certificate.pfx" -PinCode "your-pin-code" -Username "your-username" -Password "your-password"
```

### 5. Custom Parameters
```powershell
powershell -ExecutionPolicy Bypass -File "dogan-domain-scraper.ps1" -BaseUrl "https://www.dogan.com" -OutputDir "my-dogan-data" -MaxDepth 15 -Delay 2 -CertificatePath "C:\path\to\your\certificate.pfx" -PinCode "your-pin-code"
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `BaseUrl` | Starting URL for scraping | `https://www.dogan.com` |
| `OutputDir` | Output directory for scraped data | `dogan-domain-data` |
| `MaxDepth` | Maximum depth for recursive scraping | `10` |
| `Delay` | Delay between requests (seconds) | `1` |
| `CertificatePath` | Path to your PFX certificate file | (empty) |
| `PinCode` | PIN code for certificate | (empty) |
| `Username` | Username for basic authentication | (empty) |
| `Password` | Password for basic authentication | (empty) |

## Output Structure

```
dogan-domain-data/
├── html/                    # All scraped HTML pages
├── images/                  # All downloaded images
├── css/                     # All CSS files
├── js/                      # All JavaScript files
├── data/                    # Structured data (JSON)
├── metadata/                # Scraping metadata
├── certificates/            # Certificate storage
├── auth/                    # Authentication information
├── comprehensive-summary.json
├── processed-urls.txt
└── index.html              # HTML index for navigation
```

## Authentication Setup

### Certificate Authentication
1. **PFX Certificate**: Ensure you have your domain certificate in PFX format
2. **PIN Code**: Have your certificate PIN code ready
3. **Path**: Provide the full path to your certificate file

### Basic Authentication
1. **Username**: Your domain login username
2. **Password**: Your domain login password

## Security Notes
- Certificate PIN codes and passwords are handled securely
- Authentication information is stored locally only
- No credentials are transmitted to external services

## Troubleshooting

### Certificate Issues
- Ensure the certificate file path is correct
- Verify the PIN code is correct
- Check certificate validity and permissions

### Authentication Issues
- Verify username and password are correct
- Check if the domain requires specific authentication headers
- Ensure your account has proper access permissions

### Network Issues
- Check internet connectivity
- Verify domain accessibility
- Adjust delay parameters if needed

## Example Commands

### Quick Start (No Auth)
```powershell
.\dogan-domain-scraper.ps1
```

### With Certificate
```powershell
.\dogan-domain-scraper.ps1 -CertificatePath "C:\certs\dogan-cert.pfx" -PinCode "123456"
```

### With Basic Auth
```powershell
.\dogan-domain-scraper.ps1 -Username "admin" -Password "securepass123"
```

### Full Configuration
```powershell
.\dogan-domain-scraper.ps1 -BaseUrl "https://www.dogan.com" -OutputDir "dogan-backup" -MaxDepth 20 -Delay 2 -CertificatePath "C:\certs\dogan-cert.pfx" -PinCode "123456" -Username "admin" -Password "securepass123"
```

## Results
After completion, you'll have:
- Complete HTML backup of all pages
- All images, CSS, and JS files
- Structured data in JSON format
- Comprehensive scraping report
- HTML index for easy navigation
- Authentication information log

The scraper will create a complete mirror of your dogan.com domain with all content and resources.
