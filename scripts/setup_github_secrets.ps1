# Setup GitHub Actions Secrets Script
# This script helps you set up the required secrets for CI/CD

Write-Host "=== DoganAI Compliance Kit - GitHub Actions Secrets Setup ===" -ForegroundColor Green
Write-Host ""

Write-Host "To set up GitHub Actions secrets, follow these steps:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Go to your GitHub repository" -ForegroundColor Cyan
Write-Host "2. Click on 'Settings' tab" -ForegroundColor Cyan
Write-Host "3. Click on 'Secrets and variables' → 'Actions'" -ForegroundColor Cyan
Write-Host "4. Click 'New repository secret' for each secret below" -ForegroundColor Cyan
Write-Host ""

Write-Host "Required Secrets:" -ForegroundColor Yellow
Write-Host ""

Write-Host "DOCKER_REGISTRY" -ForegroundColor Green
Write-Host "Value: ghcr.io/doganai" -ForegroundColor White
Write-Host ""

Write-Host "DOCKER_USERNAME" -ForegroundColor Green
Write-Host "Value: Your GitHub username or organization name" -ForegroundColor White
Write-Host ""

Write-Host "DOCKER_PASSWORD" -ForegroundColor Green
Write-Host "Value: Your GitHub Personal Access Token" -ForegroundColor White
Write-Host "Note: Create a token at https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host ""

Write-Host "KUBECONFIG" -ForegroundColor Green
Write-Host "Value: Base64 encoded kubeconfig file" -ForegroundColor White
Write-Host "Note: Run 'kubectl config view --raw | base64' to generate" -ForegroundColor Gray
Write-Host ""

Write-Host "Optional Variables:" -ForegroundColor Yellow
Write-Host ""

Write-Host "K8S_NAMESPACE" -ForegroundColor Green
Write-Host "Value: doganai-compliance" -ForegroundColor White
Write-Host ""

Write-Host "=== Instructions ===" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Generate GitHub Personal Access Token:" -ForegroundColor Cyan
Write-Host "   - Go to https://github.com/settings/tokens" -ForegroundColor White
Write-Host "   - Click 'Generate new token (classic)'" -ForegroundColor White
Write-Host "   - Select scopes: 'repo', 'write:packages', 'read:packages'" -ForegroundColor White
Write-Host "   - Copy the token" -ForegroundColor White
Write-Host ""

Write-Host "2. Generate KUBECONFIG (if you have kubectl):" -ForegroundColor Cyan
Write-Host "   kubectl config view --raw | base64" -ForegroundColor White
Write-Host ""

Write-Host "3. Add all secrets to GitHub repository settings" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
