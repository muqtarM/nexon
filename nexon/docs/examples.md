# Examples

This page shows ready-to-run scripts and workflows that demonstrate common Nexon use cases.

---

## 1. Render-Farm Submission Script

Create a file at `examples/render_submit.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Usage: ./examples/render_submit.sh <env_name> <scene_file> [priority] [comment]
ENV_NAME="${1:-vp_render}"
SCENE_FILE="${2:-/path/to/scene.mb}"
PRIORITY="${3:-80}"
COMMENT="${4:-Automated submit}"

echo "🔧 Creating environment '${ENV_NAME}' (role=artist)"
nexon create-env "${ENV_NAME}" --role artist

echo "📦 Installing required packages"
nexon install-package "${ENV_NAME}" "houdini>=19.0" --dry-run
nexon install-package "${ENV_NAME}" "houdini>=19.0"

echo "🐳 Building Docker image for render"
nexon build-docker "${ENV_NAME}" --tag "nexon/${ENV_NAME}:render"

echo "🚀 Submitting to Deadline"
nexon render-submit "${ENV_NAME}" "${SCENE_FILE}" \
  --farm deadline \
  --options "-Priority ${PRIORITY} -Comment \"${COMMENT}\""

echo "✅ Render job submitted."
```

Make it executable:
```bash
chmod +x examples/render_submit.sh
```

---

## 2. GitHub Actions “Nexon CI” Workflow
Place this at `.github/workflows/ci_nexon.yml`:

```yaml
name: Nexon CI

on:
  workflow_dispatch:
    inputs:
      env:
        description: 'Nexon environment name'
        required: true
      script:
        description: 'Script or test harness path'
        required: true

jobs:
  run-nexon-ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Nexon CLI
        run: pip install nexon

      - name: Trigger Nexon CI job
        run: |
          nexon ci-run ${{ github.event.inputs.env }} ${{ github.event.inputs.script }} --runner github-actions
```

You can dispatch it manually via the GitHub UI or the CLI:

```bash
gh workflow run ci_nexon.yml --field env=dev --field script=tests/run_all.py
```

---

## 3. Policy-as-Code Sample Rules
Copy `docs/policies.yaml.sample` into your `~/.nexon/policies.yaml` and customize:

```yaml
# docs/policies.yaml.sample

# 1) Disallow certain packages and licenses:
disallowed_packages:
  - insecure-tool
disallowed_licenses:
  - GPL-3.0
  - AGPL-3.0

# 2) Enforce minimum versions:
min_versions:
  - package: corelib
    version: "2.1.0"

# 3) Custom assertions on environment fields:
assert:
  - id: env_role_prod
    path: "role"
    op: "eq"
    value: "prod"
    desc: "Environment role must be 'prod'"
  - id: license_key_format
    path: "env.LICENSE_KEY"
    op: "regex"
    value: "^KEY-[A-Z0-9]{16}$"
    desc: "License key must match the expected pattern"
```
Run:

```bash
nexon policy-validate myenv
nexon policy-report    myenv --output myenv_policy.html
```

---
## 4. Cron Scheduling for Backups
Although Nexon can’t directly write your crontab, use:

```bash
nexon backup-schedule
```

to print:
```text
0 2 * * * nexon backup-all >> ~/.nexon/backups/backup.log 2>&1
```

Then:
```bash
crontab -e
# paste the above line, save & exit
```

This schedules a **daily** full backup at **02:00 UTC**.