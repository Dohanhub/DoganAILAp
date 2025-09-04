$ErrorActionPreference = 'Stop'
param(
  [string]$Namespace = 'doganai',
  [string]$Release = 'doganai',
  [string]$Values = 'deploy/helm/doganai/values.yaml'
)

helm upgrade --install $Release deploy/helm/doganai -n $Namespace --create-namespace -f $Values

