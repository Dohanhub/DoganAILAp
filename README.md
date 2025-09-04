# DoganAI Compliance Kit - Build & Deployment Guide

## 1. Prepare Configuration and Secrets

- Edit `config/production.env` with all required values.
- Edit `src/deploy/k8s/secrets.yaml` and base64 encode all secret values:
  ```sh
  python scripts/k8s_secret_helper.py --encode 'your-secret-value'
  ```
  Replace the value in the YAML with the output.
- To decode a value:
  ```sh
  python scripts/k8s_secret_helper.py --decode 'base64-value'
  ```

## 2. Validate Configuration

- Run config validation before build/deploy:
  ```sh
  python scripts/validate_config.py
  ```
  Fix any errors before proceeding.

## 3. Build Docker Image

```sh
docker build -t doganai-compliance-kit:latest .
```

## 4. Test Locally (Optional)

```sh
docker run --env-file config/production.env -p 8000:8000 doganai-compliance-kit:latest
```

## 5. Push Docker Image to Registry (if using Kubernetes in the cloud)

```sh
docker tag doganai-compliance-kit:latest your-repo/doganai-compliance-kit:latest
docker push your-repo/doganai-compliance-kit:latest
```

## 6. Deploy to Kubernetes

- Use the provided deployment script:
  ```powershell
  cd src/deploy/k8s
  ./deploy-k8s.ps1 -Environment production -ClusterName "your-cluster-name"
  ```
- Or apply YAMLs manually:
  ```sh
  kubectl apply -f namespace.yaml
  kubectl apply -f storage.yaml
  kubectl apply -f configmaps.yaml
  kubectl apply -f secrets.yaml
  kubectl apply -f rbac.yaml
  kubectl apply -f deployments.yaml
  kubectl apply -f services.yaml
  kubectl apply -f ingress.yaml
  ```

## 7. Post-Deployment Validation

- Check pod and service status:
  ```sh
  kubectl get pods -n doganai-compliance
  kubectl get services -n doganai-compliance
  ```
- Check logs for errors:
  ```sh
  kubectl logs -f deployment/app-server-1 -n doganai-compliance
  ```
- Test endpoints (health, API, dashboard).

## 8. Update and Rollout

- To update config:
  ```sh
  kubectl apply -f configmaps.yaml
  kubectl rollout restart deployment/app-server-1 -n doganai-compliance
  ```
- To update image:
  ```sh
  kubectl set image deployment/app-server-1 app-server=your-repo/doganai-compliance-kit:latest -n doganai-compliance
  ```

## 9. Troubleshooting

- Use the troubleshooting section in `src/deploy/k8s/README.md` for common issues and solutions.

## 10. Automation

- Use the provided scripts for secrets and config validation.
- Integrate these steps into your CI/CD pipeline for full automation.
