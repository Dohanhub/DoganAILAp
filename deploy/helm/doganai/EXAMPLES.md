Helm Values Examples

TLS via cert-manager (nginx)
ingress:
  enabled: true
  className: nginx
  certManager:
    enabled: true
    clusterIssuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      path: /
      service: api
    - host: app.example.com
      path: /
      service: web
  tls:
    - secretName: doganai-tls
      hosts: [api.example.com, app.example.com]

NetworkPolicy allow ingress from ingress-nginx only
networkPolicy:
  enabled: true
  ingress:
    api:
      fromNamespaces: [ingress-nginx]
    web:
      fromNamespaces: [ingress-nginx]

Postgres backup to PVC and S3
backup:
  enabled: true
  image: bitnami/postgresql:15
  schedule: "0 2 * * *"
  retentionDays: 7
  env:
    DATABASE_URL: postgresql://user:pass@postgres:5432/db
  destination:
    pvc:
      create: true
      claimName: backup-data
      size: 20Gi
    s3:
      enabled: true
      bucket: my-backups
      prefix: doganai
      region: eu-west-1
      accessKeySecret: aws-creds
      secretKeySecret: aws-creds

Flagger canary (nginx)
flagger:
  enabled: true
  provider: nginx
  api:
    interval: 1m
    stepWeight: 20
    maxWeight: 60
    threshold: 5
  web:
    interval: 1m
    stepWeight: 20
    maxWeight: 60
    threshold: 5

