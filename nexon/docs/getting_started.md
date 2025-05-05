# Nexon: Getting Started
## Prerequisites
 - Python 3.8+

 - Docker (for build-and-submit workflows)

 - kubectl & kubeconfig (for Kubernetes orchestration)

 - (Optional) pg_dump/psql if you plan to use Postgres backups

 - (Optional) cron if you want scheduled backups
---
## 1. Install Nexon CLI & Server
```bash
# Install globally or in a venv
pip install nexon[all]
```
Includes `nexon` CLI plus dev-extras: Alembic, uvicorn, pytest, click-completion, etc.

---
## 2. Configure Your Environment
Create a `.env` in your project root (or Nexon server root) with at minimum:

```ini
# .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nexon
JWT_SECRET=supersecretkey
# Optional for asset tracking:
SHOTGRID_URL=https://yourstudio.shotgrid.com
SHOTGRID_SCRIPT=svc_user
SHOTGRID_KEY=shotgrid_api_key
# Optional for telemetry:
TELEMETRY_URL=https://telemetry.yoursite.com/collect
TELEMETRY_API_KEY=abcdef123456
TELEMETRY_ENABLED=true
```
On the CLI side, you can also export these directly:

```bash
export DATABASE_URL="sqlite:////path/to/nexon.db"
export JWT_SECRET="supersecretkey"
```
---
## 3. Initialize & Migrate the Server
If you’re running the **centralized Nexon service**:

```bash
# Apply database migrations
alembic upgrade head

# Launch the API + dashboard
uvicorn app.main:app --reload --port 8000
```
 - API will be available at `http://localhost:8000/`
 - Swagger UI at `http://localhost:8000/docs`

---

## 4. Core CLI Workflows
### 4.1 Create & Manage Environments
```bash
# Scaffold a new environment called "dev" with role "developer"
nexon create-env dev --role developer

# List all environments
nexon list-envs

# Activate (in your shell)
nexon activate-env dev

# Deactivate
nexon deactivate-env
```

### 4.2 Create & Publish Packages
```bash
# Scaffold a new package template "mytool" at version 0.1.0
nexon create-package mytool --version 0.1.0

# Build it (runs CMake, pip, custom steps)
nexon build-package mytool 0.1.0

# List available packages
nexon list-packages
```

### 4.3 Install & Lock
```bash
# Install "mytool-0.1.0" into "dev" env
nexon install-package dev mytool-0.1.0

# Preview what would install (dry-run)
nexon install-package dev "mypkg>=1.0,<2.0" --dry-run

# Lock the env to a reproducible file
nexon lock-env dev

# Diff two envs
nexon diff-env dev staging
```
---
## 5. Advanced Studio Features
### 5.1 Wrap & Install Arbitrary Tools
```bash
# Wrap a local tool directory as a Nexon package
nexon wrap-tool /path/to/tool --name customtool --version 1.0.0

# Now install it normally
nexon install-package dev customtool-1.0.0
```

### 5.2 Render-Farm & CI Submission
```bash
# Submit a render job (builds Docker + calls Deadline)
nexon render-submit dev /scenes/shot01.mb \
  --farm deadline \
  --options "-Priority 80"

# Trigger a CI workflow (builds Docker + GitHub Actions)
nexon ci-run dev tests/run_all.py --runner github-actions
```

### 5.3 Export for IDE Integration
```bash
# Emit a dotenv file for your env-vars
nexon env-file dev --output .env.dev

# Point VSCode at it:
#   "python.envFile": "${workspaceFolder}/.env.dev"
```
---
## 6. Web Dashboard & Graphs
1. Drop your frontend build into `nexon_web/static/` (or use the provided `index.html` + `app.js`).
2. Visit `http://localhost:8000/` to see:
   - Environments list 
   - Packages list 
   - Interactive dependency graph (D3.js)
---
## 7. Kubernetes & Cloud Orchestration
```bash
# Deploy "dev" env to Kubernetes namespace "dev"
nexon cluster-deploy dev --replicas 2 --cpu 500m --memory 1Gi \
  -e API_URL=https://api.local -e MODE=dev

# Expose it via Ingress
nexon cluster-expose dev example.mycompany.com --path /

# Enable autoscaling (1–5 replicas @75% CPU)
nexon cluster-autoscale dev --min-replicas 1 --max-replicas 5 --cpu-percent 75

# Tear down
nexon cluster-destroy dev
nexon cluster-unautoscale dev
```
---
## 8. Compliance & Policy-as-Code
```bash
# Validate against policies.yaml
nexon policy-validate dev

# Generate a polished HTML report
nexon policy-report dev --output dev_compliance.html
```
Sample rules in `docs/policies.yaml.sample`.

---
## 9. Monitoring & Metrics
- Prometheus: scrape `http://localhost:8000/metrics` for:
  - `nexon_environments_total`
  - `nexon_packages_total`
  - `nexon_audit_entries_total`
- Telemetry: ensure your `telemetry_url` is set to capture CLI usage events.

---
## 10. Backup & Disaster Recovery
```bash
# Immediate backup (DB + all on-disk)
nexon backup-all

# Restore from a backup archive
nexon restore ~/.nexon/backups/nexon_backup_20250505T020000Z.tar.gz

# Schedule daily backups via cron
nexon backup-schedule
```