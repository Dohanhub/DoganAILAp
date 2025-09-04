#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy DoganAI Compliance Kit to Kubernetes Cluster
    
.DESCRIPTION
    This script deploys the complete DoganAI Compliance Kit Strong Application Engine
    to a Kubernetes cluster with proper layering, security, and monitoring.
    
.PARAMETER Environment
    Deployment environment (dev, staging, production)
    
.PARAMETER ClusterName
    Kubernetes cluster name
    
.PARAMETER Namespace
    Target namespace (default: doganai-compliance)
    
.PARAMETER UseHelm
    Use Helm chart for deployment
    
.PARAMETER SkipPrerequisites
    Skip prerequisite checks
    
.PARAMETER SkipMonitoring
    Skip monitoring stack deployment
    
.EXAMPLE
    .\deploy-k8s.ps1 -Environment production -ClusterName "doganai-cluster"
    .\deploy-k8s.ps1 -Environment dev -UseHelm
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "production")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$ClusterName = "doganai-cluster",
    
    [Parameter(Mandatory=$false)]
    [string]$Namespace = "doganai-compliance",
    
    [Parameter(Mandatory=$false)]
    [switch]$UseHelm,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipPrerequisites,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipMonitoring
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions for output
function Write-Info { Write-Host "ℹ️  $($args[0])" -ForegroundColor Cyan }
function Write-Success { Write-Host "✅ $($args[0])" -ForegroundColor Green }
function Write-Warning { Write-Host "⚠️  $($args[0])" -ForegroundColor Yellow }
function Write-Error { Write-Host "❌ $($args[0])" -ForegroundColor Red }

# Banner
Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║           🚀 DoganAI K8s Deployment Engine                 ║
║                                                              ║
║  Environment: $($Environment.ToUpper().PadRight(42)) ║
║  Cluster: $($ClusterName.PadRight(42)) ║
║  Namespace: $($Namespace.PadRight(42)) ║
║  Architecture: Strong Application Engine                    ║
║  Capacity: 2,000-3,000 concurrent users                    ║
║  Scale: Enterprise + IBM Demo Ready                         ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

Write-Info "Starting Kubernetes deployment of DoganAI Compliance Kit..."

# Check prerequisites
if (-not $SkipPrerequisites) {
    Write-Info "Checking prerequisites..."
    
    # Check kubectl
    try {
        $kubectlVersion = kubectl version --client --short
        Write-Success "kubectl: $kubectlVersion"
    } catch {
        Write-Error "kubectl is not installed or not in PATH. Please install kubectl."
        exit 1
    }
    
    # Check kubectl connection
    try {
        $clusterInfo = kubectl cluster-info
        Write-Success "Connected to Kubernetes cluster"
        Write-Info "Cluster Info: $clusterInfo"
    } catch {
        Write-Error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    }
    
    # Check Helm if using Helm deployment
    if ($UseHelm) {
        try {
            $helmVersion = helm version --short
            Write-Success "Helm: $helmVersion"
        } catch {
            Write-Error "Helm is not installed or not in PATH. Please install Helm."
            exit 1
        }
    }
    
    # Check cluster resources
    Write-Info "Checking cluster resources..."
    try {
        $nodes = kubectl get nodes -o json | ConvertFrom-Json
        $totalCPU = 0
        $totalMemory = 0
        
        foreach ($node in $nodes.items) {
            $cpu = [int]($node.status.capacity.'cpu' -replace 'm', '')
            $memory = [int]($node.status.capacity.'memory' -replace 'Ki', '')
            $totalCPU += $cpu
            $totalMemory += $memory
        }
        
        $totalMemoryGB = [math]::Round($totalMemory / 1024 / 1024, 2)
        Write-Info "Cluster Resources:"
        Write-Info "  Total CPU: $($totalCPU)m"
        Write-Info "  Total Memory: $totalMemoryGB Gi"
        
        if ($totalCPU -lt 8000) {
            Write-Warning "Recommended minimum CPU: 8000m (Current: $($totalCPU)m)"
        }
        
        if ($totalMemoryGB -lt 16) {
            Write-Warning "Recommended minimum memory: 16GB (Current: $totalMemoryGB GB)"
        }
    } catch {
        Write-Warning "Could not check cluster resources"
    }
}

# Create namespaces
Write-Info "Creating namespaces..."
$namespaces = @(
    "doganai-compliance",
    "doganai-monitoring",
    "doganai-logging"
)

foreach ($ns in $namespaces) {
    try {
        kubectl create namespace $ns --dry-run=client -o yaml | kubectl apply -f -
        Write-Success "Namespace '$ns' created/updated"
    } catch {
        Write-Warning "Could not create namespace '$ns': $($_.Exception.Message)"
    }
}

# Set context namespace
Write-Info "Setting context namespace to '$Namespace'..."
kubectl config set-context --current --namespace=$Namespace

# Deploy using Helm or direct YAML
if ($UseHelm) {
    Write-Info "Deploying using Helm chart..."
    
    try {
        # Add Helm repository if needed
        # helm repo add doganai https://charts.dogan-ai.com
        
        # Install/upgrade the chart
        helm upgrade --install doganai-compliance-kit ./k8s/helm-chart `
            --namespace $Namespace `
            --create-namespace `
            --set global.environment=$Environment `
            --set global.clusterDomain=$ClusterName `
            --wait `
            --timeout 10m
        
        Write-Success "Helm deployment completed successfully!"
        
    } catch {
        Write-Error "Helm deployment failed: $($_.Exception.Message)"
        exit 1
    }
    
} else {
    Write-Info "Deploying using direct YAML files..."
    
    # Deploy in order of dependencies
    $deploymentOrder = @(
        "namespace.yaml",
        "configmaps.yaml",
        "secrets.yaml",
        "storage.yaml",
        "rbac.yaml",
        "deployments.yaml",
        "services.yaml",
        "ingress.yaml"
    )
    
    foreach ($file in $deploymentOrder) {
        $filePath = "k8s/$file"
        if (Test-Path $filePath) {
            Write-Info "Deploying $file..."
            try {
                kubectl apply -f $filePath
                Write-Success "$file deployed successfully"
            } catch {
                Write-Error "Failed to deploy $file: $($_.Exception.Message)"
                exit 1
            }
        } else {
            Write-Warning "File $file not found, skipping..."
        }
    }
}

# Wait for deployments to be ready
Write-Info "Waiting for deployments to be ready..."
$maxWaitTime = 600  # 10 minutes
$startTime = Get-Date
$ready = $false

while (-not $ready -and ((Get-Date) - $startTime).TotalSeconds -lt $maxWaitTime) {
    try {
        $deployments = kubectl get deployments -n $Namespace -o json | ConvertFrom-Json
        $totalDeployments = $deployments.items.Count
        $readyDeployments = ($deployments.items | Where-Object { $_.status.readyReplicas -eq $_.spec.replicas }).Count
        
        Write-Info "Deployments: $readyDeployments/$totalDeployments ready"
        
        if ($readyDeployments -eq $totalDeployments) {
            $ready = $true
            Write-Success "All deployments are ready!"
        } else {
            Start-Sleep -Seconds 15
        }
    } catch {
        Start-Sleep -Seconds 15
    }
}

if (-not $ready) {
    Write-Warning "Some deployments may not be fully ready. Check status for details."
}

# Check service status
Write-Info "Checking service status..."
try {
    kubectl get services -n $Namespace
} catch {
    Write-Warning "Could not get service status"
}

# Check pod status
Write-Info "Checking pod status..."
try {
    kubectl get pods -n $Namespace
} catch {
    Write-Warning "Could not get pod status"
}

# Test endpoints
Write-Info "Testing key endpoints..."
$endpoints = @(
    "http://localhost:8080/health",
    "http://localhost:3000",
    "http://localhost:5601"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 10 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Success "✅ $endpoint - OK"
        } else {
            Write-Warning "⚠️  $endpoint - Status: $($response.StatusCode)"
        }
    } catch {
        Write-Warning "⚠️  $endpoint - Unavailable"
    }
}

# Display access information
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                    🎉 K8s DEPLOYMENT COMPLETE!              ║
╚══════════════════════════════════════════════════════════════╝

🌐 Application Access:
   Main Dashboard: https://compliance.dogan-ai.com
   API Endpoint: https://api.dogan-ai.com
   Admin Panel: https://admin.dogan-ai.com

🔍 Monitoring & Analytics:
   Grafana: https://monitoring.dogan-ai.com
   Prometheus: https://prometheus.dogan-ai.com
   Kibana: https://logs.dogan-ai.com

📊 Health Checks:
           kubectl get pods -n $($Namespace)
        kubectl get services -n $($Namespace)
        kubectl get ingress -n $($Namespace)

🔧 Management Commands:
   View Logs: kubectl logs -f deployment/app-server-1 -n $($Namespace)
   Scale App: kubectl scale deployment app-server-1 --replicas=5 -n $($Namespace)
   Update Config: kubectl apply -f k8s/configmaps.yaml
   Delete All: kubectl delete namespace $($Namespace)

📈 Scaling:
   kubectl autoscale deployment app-server-1 --cpu-percent=70 --min=3 --max=10 -n $($Namespace)

"@ -ForegroundColor Green

# Display cluster information
Write-Info "Cluster Information:"
try {
    kubectl cluster-info
} catch {
    Write-Warning "Could not get cluster info"
}

Write-Success "Kubernetes deployment completed successfully!"
Write-Info "Your DoganAI Compliance Kit is now running on Kubernetes!"
Write-Info "Next steps: Configure your compliance data and start using the platform."

# Optional: Open dashboard
$openDashboard = Read-Host "Would you like to open the Kubernetes dashboard? (y/n)"
if ($openDashboard -eq "y" -or $openDashboard -eq "Y") {
    try {
        Start-Process "kubectl" -ArgumentList "proxy" -WindowStyle Hidden
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
        Write-Info "Kubernetes dashboard opened in browser"
    } catch {
        Write-Warning "Could not open Kubernetes dashboard"
    }
}
