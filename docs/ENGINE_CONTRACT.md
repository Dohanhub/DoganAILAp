# Modular Engine Contract

1. All features/modules must be standalone and pluggable.
2. No placeholder or demo code is allowed.
3. Each module must have a manifest file describing:
   - Name, version, description
   - Exposed interfaces (APIs, UI components)
   - Dependencies (other modules, services)
4. The engine must support dynamic composition of modules (vertical/horizontal).
5. All code must follow best practices and be production-ready.
6. The contract is enforced by `engine/contract_enforcer.py` and CI/CD.
