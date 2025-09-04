External Secrets Operator (ESO) Examples

AWS Secrets Manager
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-sm
spec:
  provider:
    aws:
      service: SecretsManager
      region: eu-central-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-creds
            key: AWS_ACCESS_KEY_ID
          secretAccessKeySecretRef:
            name: aws-creds
            key: AWS_SECRET_ACCESS_KEY

Helm values:
externalSecrets:
  enabled: true
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-sm
  data:
    - secretKey: SECRET_KEY
      remoteRef: { key: doganai/secret-key }
    - secretKey: API_KEY
      remoteRef: { key: doganai/api-key }
    - secretKey: DATABASE_URL
      remoteRef: { key: doganai/database-url }

Azure Key Vault
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: azure-kv
spec:
  provider:
    azurekv:
      tenantId: <tenant-id>
      vaultUrl: https://<vault-name>.vault.azure.net/
      authSecretRef:
        clientId:
          name: azure-kv-creds
          key: ClientID
        clientSecret:
          name: azure-kv-creds
          key: ClientSecret

GCP Secret Manager
---
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: gcp-sm
spec:
  provider:
    gcpsm:
      projectID: <project-id>
      auth:
        secretRef:
          secretAccessKeySecretRef:
            name: gcp-creds
            key: credentials.json

