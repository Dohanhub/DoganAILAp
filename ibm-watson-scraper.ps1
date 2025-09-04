# IBM Watson Platform & Saudi Arabia Market Scraper
param(
    [string]$OutputPath = "D:\Dogan-Ai\Development\IBM",
    [switch]$IncludeSaudiMarket = $true
)

# Create output directory
if (!(Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}

Write-Host "Starting IBM Watson Platform & Saudi Arabia Market Scraping..." -ForegroundColor Green

# IBM Watson Platform URLs to scrape
$watsonUrls = @(
    "https://www.ibm.com/watson",
    "https://www.ibm.com/watson/ai",
    "https://www.ibm.com/watson/ai-platform",
    "https://www.ibm.com/watson/ai-solutions",
    "https://www.ibm.com/watson/ai-tools",
    "https://www.ibm.com/watson/ai-services",
    "https://www.ibm.com/watson/ai-software",
    "https://www.ibm.com/watson/ai-platform/studio",
    "https://www.ibm.com/watson/ai-platform/assistant",
    "https://www.ibm.com/watson/ai-platform/discovery",
    "https://www.ibm.com/watson/ai-platform/natural-language-understanding",
    "https://www.ibm.com/watson/ai-platform/speech-to-text",
    "https://www.ibm.com/watson/ai-platform/text-to-speech",
    "https://www.ibm.com/watson/ai-platform/visual-recognition",
    "https://www.ibm.com/watson/ai-platform/language-translator",
    "https://www.ibm.com/watson/ai-platform/personality-insights",
    "https://www.ibm.com/watson/ai-platform/tone-analyzer",
    "https://www.ibm.com/watson/ai-platform/conversation",
    "https://www.ibm.com/watson/ai-platform/knowledge-studio"
)

# Saudi Arabia Market Research URLs
$saudiMarketUrls = @(
    "https://www.ibm.com/case-studies/saudi-arabia",
    "https://www.ibm.com/middle-east",
    "https://www.ibm.com/middle-east/saudi-arabia",
    "https://www.ibm.com/thought-leadership/saudi-arabia",
    "https://www.ibm.com/industries/energy/saudi-arabia",
    "https://www.ibm.com/industries/financial-services/saudi-arabia",
    "https://www.ibm.com/industries/healthcare/saudi-arabia",
    "https://www.ibm.com/industries/retail/saudi-arabia",
    "https://www.ibm.com/industries/telecommunications/saudi-arabia"
)

# Market research and benchmark URLs
$marketResearchUrls = @(
    "https://www.ibm.com/thought-leadership",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/insights",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/reports",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/studies",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/benchmarks",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/middle-east",
    "https://www.ibm.com/thought-leadership/ibm-institute-for-business-value/saudi-arabia"
)

$allUrls = $watsonUrls + $marketResearchUrls
if ($IncludeSaudiMarket) {
    $allUrls += $saudiMarketUrls
}

# Function to clean filename
function Get-SafeFileName {
    param([string]$Url)
    $filename = $Url -replace "https?://", "" -replace "www\.", "" -replace "[^\w\-\.]", "_"
    return $filename
}

# Function to extract content from URL
function Extract-ContentFromUrl {
    param([string]$Url, [string]$OutputDir)
    
    try {
        Write-Host "Scraping: $Url" -ForegroundColor Yellow
        
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30
        $html = $response.Content
        $baseUrl = $response.BaseResponse.ResponseUri
        
        # Create safe filename
        $filename = Get-SafeFileName $Url
        $htmlPath = "$OutputDir\$filename.html"
        
        # Save HTML content
        $html | Out-File -FilePath $htmlPath -Encoding UTF8
        
        # Extract text content
        $textContent = $html -replace '<[^>]+>', ' ' -replace '\s+', ' ' -replace '&[^;]+;', ' '
        $textPath = "$OutputDir\$filename.txt"
        $textContent | Out-File -FilePath $textPath -Encoding UTF8
        
        # Extract links
        $linkPattern = 'href=["'']([^"'']*)["'']'
        $linkMatches = [regex]::Matches($html, $linkPattern)
        $links = @()
        
        foreach ($match in $linkMatches) {
            $link = $match.Groups[1].Value
            if ($link -match '^https?://') {
                $links += $link
            } elseif ($link -match '^/') {
                $links += "$($baseUrl.Scheme)://$($baseUrl.Host)$link"
            }
        }
        
        # Extract images
        $imgPattern = 'src=["'']([^"'']*)["'']'
        $imgMatches = [regex]::Matches($html, $imgPattern)
        $images = @()
        
        foreach ($match in $imgMatches) {
            $img = $match.Groups[1].Value
            if ($img -match '^https?://') {
                $images += $img
            } elseif ($img -match '^/') {
                $images += "$($baseUrl.Scheme)://$($baseUrl.Host)$img"
            }
        }
        
        # Extract metadata
        $title = ""
        $titleMatch = [regex]::Match($html, '<title[^>]*>([^<]*)</title>')
        if ($titleMatch.Success) {
            $title = $titleMatch.Groups[1].Value.Trim()
        }
        
        $description = ""
        $descMatch = [regex]::Match($html, '<meta[^>]*name=["'']description["''][^>]*content=["'']([^"'']*)["'']')
        if ($descMatch.Success) {
            $description = $descMatch.Groups[1].Value.Trim()
        }
        
        # Create metadata object
        $metadata = @{
            "Url" = $Url
            "Title" = $title
            "Description" = $description
            "Links" = ($links | Select-Object -Unique)
            "Images" = ($images | Select-Object -Unique)
            "ScrapeDate" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        
        # Save metadata as JSON
        $metadataPath = "$OutputDir\$filename-metadata.json"
        $metadata | ConvertTo-Json -Depth 10 | Out-File -FilePath $metadataPath -Encoding UTF8
        
        return @{
            "Success" = $true
            "Url" = $Url
            "Files" = @($htmlPath, $textPath, $metadataPath)
        }
        
    } catch {
        Write-Host "Error scraping $Url`: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            "Success" = $false
            "Url" = $Url
            "Error" = $_.Exception.Message
        }
    }
}

# Main scraping process
$results = @()
$successCount = 0
$errorCount = 0

foreach ($url in $allUrls) {
    $result = Extract-ContentFromUrl -Url $url -OutputDir $OutputPath
    $results += $result
    
    if ($result.Success) {
        $successCount++
    } else {
        $errorCount++
    }
    
    # Add delay to be respectful
    Start-Sleep -Seconds 2
}

# Generate summary report
$summary = @{
    "TotalUrls" = $allUrls.Count
    "Successful" = $successCount
    "Failed" = $errorCount
    "ScrapeDate" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "OutputPath" = $OutputPath
    "Results" = $results
}

$summaryPath = "$OutputPath\scraping-summary.json"
$summary | ConvertTo-Json -Depth 10 | Out-File -FilePath $summaryPath -Encoding UTF8

# Generate text summary
$textSummary = @"
IBM WATSON PLATFORM & SAUDI ARABIA MARKET SCRAPING SUMMARY
========================================================

Scrape Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Output Directory: $OutputPath

STATISTICS:
- Total URLs Attempted: $($allUrls.Count)
- Successfully Scraped: $successCount
- Failed: $errorCount
- Success Rate: $([math]::Round(($successCount / $allUrls.Count) * 100, 2))%

WATSON PLATFORM URLS:
$(($watsonUrls | ForEach-Object { "- $_" }) -join "`n")

MARKET RESEARCH URLS:
$(($marketResearchUrls | ForEach-Object { "- $_" }) -join "`n")

$(if ($IncludeSaudiMarket) { "SAUDI ARABIA MARKET URLS:`n$(($saudiMarketUrls | ForEach-Object { "- $_" }) -join "`n")`n" })

FAILED URLS:
$(($results | Where-Object { -not $_.Success } | ForEach-Object { "- $($_.Url): $($_.Error)" }) -join "`n")

Files generated for each successful URL:
- [filename].html (raw HTML)
- [filename].txt (extracted text)
- [filename]-metadata.json (metadata, links, images)
"@

$textSummary | Out-File -FilePath "$OutputPath\scraping-summary.txt" -Encoding UTF8

Write-Host "`nScraping completed!" -ForegroundColor Green
Write-Host "Total URLs: $($allUrls.Count)" -ForegroundColor Yellow
Write-Host "Successful: $successCount" -ForegroundColor Green
Write-Host "Failed: $errorCount" -ForegroundColor Red
Write-Host "Output directory: $OutputPath" -ForegroundColor Cyan
Write-Host "Summary files:" -ForegroundColor Cyan
Write-Host "  - $OutputPath\scraping-summary.json" -ForegroundColor White
Write-Host "  - $OutputPath\scraping-summary.txt" -ForegroundColor White
