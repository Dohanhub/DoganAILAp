# Deploy to Kubernetes Task

Task: Deploy application to Kubernetes cluster.

Steps:
1) Run `make kube-apply`.
2) Check pod status: `kubectl get pods -n $K8S_NAMESPACE`.
3) Monitor rollout: `kubectl rollout status deploy/doganai-compliance-kit -n $K8S_NAMESPACE`.
4) Verify service is accessible.

Expected outcome: Application successfully deployed and running in Kubernetes.
