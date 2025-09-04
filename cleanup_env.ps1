# Script to clean up environment files and vendor directories

# Define patterns to search for
$patterns = @(
    "*.env*",
    ".env*",
    "venv",
    ".venv",
    "env",
    ".env",
    "vendor",
    "node_modules",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "build",
    "develop-eggs",
    "dist",
    "downloads",
    "eggs",
    ".eggs",
    "lib",
    "lib64",
    "parts",
    "sdist",
    "var",
    "wheels",
    "*.egg-info",
    ".installed.cfg",
    "*.egg",
    ".pytest_cache",
    ".mypy_cache",
    ".coverage",
    "htmlcov"
)

# Search for files and directories matching patterns
$itemsToRemove = @()

foreach ($pattern in $patterns) {
    $itemsToRemove += Get-ChildItem -Path . -Recurse -Force -Include $pattern -ErrorAction SilentlyContinue
}

# Remove duplicates
$itemsToRemove = $itemsToRemove | Sort-Object -Property FullName -Unique

# Display what will be removed
Write-Host "The following items will be removed:"
$itemsToRemove | ForEach-Object { 
    $type = if ($_.PSIsContainer) { "Directory" } else { "File" }
    Write-Host "- $type: $($_.FullName)" 
}

# Ask for confirmation
$confirmation = Read-Host "Do you want to proceed with deletion? (y/n)"
if ($confirmation -eq 'y') {
    # Remove items
    $itemsToRemove | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleanup completed."
} else {
    Write-Host "Cleanup cancelled."
}
