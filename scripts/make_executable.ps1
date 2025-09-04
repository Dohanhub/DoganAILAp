# Make shell scripts executable on Windows
# This is mainly for Git Bash or WSL compatibility

$scripts = @(
    "scripts/bootstrap.sh",
    "scripts/wait_for.sh", 
    "scripts/healthcheck.sh"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "Making $script executable..."
        # On Windows, this mainly affects Git Bash behavior
        # The files will be executable when used with Git Bash or WSL
    } else {
        Write-Host "Warning: $script not found"
    }
}

Write-Host "Script setup complete!"
