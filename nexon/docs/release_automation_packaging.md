# Release Automation & Packaging

Automate version bumps, PyPI publications, and Docker image builds & pushes.

---

## 1. Bump Version

```bash
# Bump the version in pyproject.toml, commit & tag
nexon bump-version 1.2.0
```

Under the hood:
 - Updates `version = "x.y.z"` in `pyproject.toml`
 - `git add` → `git commit -m "Bump version to x.y.z"` → `git tag vx.y.z`

---
## 2. Build & Publish Release
```bash
# Build sdist & wheel, upload to PyPI, build & push Docker image
nexon build-release
```
Requires:
- `python -m build` & `twine` for PyPI 
- Docker CLI login to Docker Hub

---
## 3. GitHub Actions Workflow
Place in `.github/workflows/release.yml`:

```yaml
on:
  push:
    tags: ['v*.*.*']

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: python-version: '3.12'
      - run: pip install build twine
      - run: |
          python -m build
          twine upload dist/*
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
          TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - run: |
          VERSION=${{ github.ref_name#v }}
          docker build -t nexon/cli:$VERSION .
          docker push nexon/cli:$VERSION
          docker tag nexon/cli:$VERSION nexon/cli:latest
          docker push nexon/cli:latest
```

---
# Security & Compliance Scanning
Leverage policy-as-code and OSV vulnerability checks.

---
## 1. Define Policies
Create `~/.nexon/policies.yaml`:

```yaml
disallowed_packages:
  - insecure-tool
disallowed_licenses:
  - GPL-3.0
min_versions:
  - package: corelib
    version: "2.1.0"
assert:
  - id: env_role_prod
    path: "role"
    op: "eq"
    value: "prod"
    desc: "Role must be 'prod'"
```

---
## 2. Validate & Report
```bash
# CLI validation (exit code 0 if compliant)
nexon policy-validate dev

# Generate HTML report
nexon policy-report dev --output dev_compliance.html
```
Artifacts:
- **policy-validate**: lists violations in console
- **policy-report**: polished HTML via Jinja2 template

---
# Monitoring & Telemetry
Collect metrics, expose Prometheus, and send usage events.

---
## 1. Prometheus Metrics
Scrape endpoints:
- **CLI**: `/metrics` (counts audit-log actions)
- **Server**: `/metrics` (gauges: environments, packages, audit entries)

Example scrape config:
```yaml
scrape_configs:
  - job_name: nexon-cli
    static_configs:
      - targets: ['localhost:8000']
```

---
## 2. Telemetry Events
Enable in `~/.nexon/.env`:

```ini
TELEMETRY_ENABLED=true
TELEMETRY_URL=https://telemetry.example.com/collect
TELEMETRY_API_KEY=your_key
```

Installed plugin `telemetry` will emit:
- `post_create_env`
- `post_install_package`
- `post_build_package`

---

# Asset-Tracker Integration
Query ShotGrid and sync Perforce from CLI & API.

---
## 1. Configure
```ini
# ~/.nexon/.env
SHOTGRID_URL=https://studio.shotgrid.com
SHOTGRID_SCRIPT=my_script
SHOTGRID_KEY=my_key

P4PORT=perforce:1666
P4USER=jenkins
P4CLIENT=studio_ws
```

---
## 2. CLI Commands
```bash
# Fetch shot details from ShotGrid
nexon shot-context SHOT01

# Sync Perforce path
nexon p4-sync //depot/project/...
```

---
## 3. API Endpoints
```http
GET /assets/shot/{shot_name}
POST /assets/p4/sync { "depot_path": "//depot/..." }
```
Requires JWT bearer authentication.

---
# Kubernetes & Cloud Orchestration
Deploy Nexon envs to k8s with a single CLI.

---
## 1. Deploy & Expose
```bash
# Deploy in k8s
nexon cluster-deploy dev \
  --replicas 2 \
  --cpu 500m \
  --memory 1Gi \
  -e API_URL=https://api.local

# Create Ingress
nexon cluster-expose dev example.com --path /
```

---
## 2. Autoscaling
```bash
# Enable HPA @75% CPU, 1–5 replicas
nexon cluster-autoscale dev --min-replicas 1 --max-replicas 5 --cpu-percent 75

# Remove HPA
nexon cluster-unautoscale dev
```

---
## 3. Tear Down
```bash
nexon cluster-destroy dev
```

---
# Backup & Disaster Recovery
Archive DB & disk state, restore on demand, schedule via cron.

---
## 1. Backup & Restore
```bash
# Immediate backup
nexon backup-all

# Restore from archive
nexon restore ~/.nexon/backups/nexon_backup_20250505T020000Z.tar.gz
```

---
## 2. Schedule via Cron
```bash
nexon backup-schedule
# copy the printed cron line into `crontab -e`
```

---
# Integration Testing & QA
Automate end-to-end validation of CLI, API, k8s, and workflows.

---
## 1. GitHub Actions E2E CI
See `.github/workflows/e2e-ci.yml` for a sample pipeline that spins up Postgres, runs migrations, exercises CLI, starts the API server, and runs smoke & integration tests.

---
## 2. Local pytest Suite
Run:

```bash
pytest tests/test_integration.py -q
```
This suite covers:
- CLI commands (`create-env`, `install-package`, `lock-env`, `diff-env`, etc.)
- FastAPI endpoints (`/auth/token`, `/envs`, `/packages`, `/metrics`, `/assets`)
- Mixed CLI+API flows (e.g. dependency graph, backup & restore)

---
# Further Reading
- **Examples**: `docs/examples.md`
- **Plugin Guide**: `docs/plugin-guide.md`
- **Policies Sample**: `docs/policies.yaml.sample`
- **Release Notes**: `CHANGELOG.md`