Offline pre-commit mirrors

This repository vendors tarball mirrors of the ruff, black, and mypy pre-commit hooks under `tools/pre-commit-mirrors/`.

Updating mirrors

1. Obtain the upstream `.pre-commit-hooks.yaml` for the desired version.
2. Create a directory named after the hook and version (e.g. `ruff-pre-commit-v0.6.9`).
3. Place the `.pre-commit-hooks.yaml` in that directory with `language: system` so pre-commit uses locally-installed binaries.
4. Archive the directory:

   tar -czf tools/pre-commit-mirrors/ruff-pre-commit-v0.6.9.tar.gz ruff-pre-commit-v0.6.9

5. Compute the SHA256 checksum and update `.pre-commit-config.yaml`:

   sha256sum tools/pre-commit-mirrors/ruff-pre-commit-v0.6.9.tar.gz

6. Point `.pre-commit-config.yaml` at the tarball using a `file://` URL and the checksum.

CI usage

CI environments can reuse the mirrors by checking out the repository and running `pre-commit run` as usual. Because the mirrors use `language: system`, ensure `ruff`, `black`, and `mypy` are installed on the CI image.
