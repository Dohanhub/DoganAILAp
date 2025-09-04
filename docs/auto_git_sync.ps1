# Auto Git Sync Script
# Adds, commits, pushes, and pulls every minute

while ($true) {
    git add .
    $status = git status --porcelain
    if ($status) {
        $msg = "Auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git commit -m $msg
        git push
    }
    git pull
    Start-Sleep -Seconds 60
}
