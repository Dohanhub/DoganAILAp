import os


def svc_url(name: str, ns: str | None = None, port: int | None = None) -> str:
    ns = ns or os.getenv("K8S_NAMESPACE", os.getenv("NAMESPACE", "default"))
    scheme = os.getenv("K8S_SCHEME", "http")
    host = f"{scheme}://{name}.{ns}.svc.cluster.local"
    return f"{host}:{port}" if port else host

