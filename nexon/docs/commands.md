# Nexon CLI Commands Reference

_All commands are invoked via the `nexon` CLI._

---

## Phase 1 – Essential Foundation

| Command                         | Description                                                        | Example                                                     |
|---------------------------------|--------------------------------------------------------------------|-------------------------------------------------------------|
| `nexon create-env <name>`       | Scaffold a new environment (creates `<name>.yaml`).                | `nexon create-env demo --role animator`                     |
| `nexon list-envs`               | List all existing environments.                                    | `nexon list-envs`                                           |
| `nexon activate-env <name>`     | Activate an environment (sets env-vars in your shell).             | `nexon activate-env demo`                                   |
| `nexon deactivate-env`          | Deactivate the current Nexon environment (restores shell).         | `nexon deactivate-env`                                      |
| `nexon lock-env <name>`         | Freeze an environment to a lockfile (`<name>.lock.yaml`).          | `nexon lock-env demo`                                       |
| `nexon create-package <pkg>`    | Scaffold a versioned package template.                             | `nexon create-package mytool --version 0.1.0`               |
| `nexon list-packages`           | List all packages and available versions.                          | `nexon list-packages`                                       |
| `nexon build-package <pkg> <v>` | Run the build steps (CMake, pip, custom) for a package.            | `nexon build-package mytool 0.1.0`                          |
| `nexon install-package <env> <req>` | Install a specific package into an env.                          | `nexon install-package demo mytool-0.1.0`                   |
| `nexon uninstall-package <env> <pkg-v>` | Remove a package-version from an environment.               | `nexon uninstall-package demo mytool-0.1.0`                 |
| `nexon diff-env <envA> <envB>`  | Show added/removed packages and role changes between two envs.     | `nexon diff-env dev staging`                                |
| `nexon build-docker <env>`      | Containerize an environment into a Docker image.                   | `nexon build-docker demo --tag demo:latest`                 |
| `nexon env-file <env>`          | Export env-vars in dotenv format (stdout or via `-o`).             | `nexon env-file dev --output .env.dev`                      |

---

## Phase 2 – Studio Must-Haves

| Command                                    | Description                                                         | Example                                                              |
|--------------------------------------------|---------------------------------------------------------------------|----------------------------------------------------------------------|
| `nexon install-package <env> <req> --dry-run` | Preview which packages *would* be added, without modifying env.     | `nexon install-package demo "mypkg>=1.2,<2.0" --dry-run`             |
| `nexon wrap-tool <path> --name <n> --version <v>` | Wrap any folder as a Nexon package (auto-detects executables).    | `nexon wrap-tool /path/to/tool --name custom --version 1.0.0`        |
| `nexon lock-env <env>`                     | Write a lockfile capturing exact package versions.                  | `nexon lock-env dev`                                                 |
| `nexon diff-env <env1> <env2>`             | Compare two environments or env vs lockfile.                        | `nexon diff-env staging staging.lock.yaml`                           |

---

## Phase 3 – High-Impact Extensions

| Command                          | Description                                                             | Example                                                           |
|----------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------|
| `nexon render-submit <env> <scene>` | Build env into Docker and submit a render job to a farm (e.g. Deadline). | `nexon render-submit prod /scenes/shot01.mb --farm deadline`     |
| `nexon ci-run <env> <script>`    | Build env into Docker and trigger a CI workflow (e.g. GitHub Actions).  | `nexon ci-run prod tests/run_all.py --runner github-actions`      |
| `nexon completion <shell>`       | Generate—or install—shell completion code (`bash`, `zsh`, etc.).        | `nexon completion bash --install`                                 |
| `nexon shell <env>`              | Spawn a subshell with the specified env activated.                     | `nexon shell prod`                                                |
| `nexon bump-version <v>`         | Update `pyproject.toml`, commit & tag a new version.                    | `nexon bump-version 1.2.0`                                        |
| `nexon build-release`            | Build & publish to PyPI; build & push Docker image tagged by version.   | `nexon build-release`                                             |
| `nexon security-scan <env>`      | Scan for disallowed packages/licenses and known OSV vulnerabilities.     | `nexon security-scan prod`                                        |

---

## Phase 4 – Plugin, Notifications & Telemetry

| Command                       | Description                                                       | Example                                              |
|-------------------------------|-------------------------------------------------------------------|------------------------------------------------------|
| `nexon list-layers`           | List your global, team, project, and user configuration layers.   | `nexon list-layers`                                  |
| `nexon create-layer`          | Create/overwrite a layer (`global`, `team`, `project`, `user`).   | `nexon create-layer team fx fx.yaml`                 |
| `nexon show-effective`        | Show merged config: global→team→project→user→env.                 | `nexon show-effective shot01 fx seq01 --user alice` |
| `nexon policy-validate <env>` | Validate an env against policy-as-code rules.                     | `nexon policy-validate dev`                          |
| `nexon policy-report <env>`   | Generate a polished HTML compliance report.                       | `nexon policy-report prod --output report.html`      |

---

## Phase 5 – Enterprise & Cloud Integrations

| Command                              | Description                                                           | Example                                                                  |
|--------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------|
| `nexon shot-context <shot>`          | Query ShotGrid for context on a shot.                                 | `nexon shot-context SHOT01`                                              |
| `nexon p4-sync <depot_path>`         | Sync a Perforce path in your current workspace.                       | `nexon p4-sync //depot/project/...`                                      |
| `nexon cluster-deploy <env>`         | Deploy or update a k8s Deployment & Service for your env.             | `nexon cluster-deploy prod --replicas 2 --cpu 500m --memory 1Gi`         |
| `nexon cluster-expose <env> <host>`  | Create/update an Ingress mapping host/path → your service.            | `nexon cluster-expose prod example.com --path /`                        |
| `nexon cluster-autoscale <env>`      | Enable HPA (min/max replicas, CPU threshold).                         | `nexon cluster-autoscale prod --min-replicas 1 --max-replicas 5`        |
| `nexon cluster-unautoscale <env>`    | Remove the HorizontalPodAutoscaler for an env.                        | `nexon cluster-unautoscale prod`                                        |
| `nexon cluster-list`                 | List all Nexon k8s deployments and replica counts.                    | `nexon cluster-list`                                                     |
| `nexon cluster-destroy <env>`        | Tear down the k8s Deployment & Service for the env.                   | `nexon cluster-destroy prod`                                             |
| `nexon backup-all`                   | Dump DB + tar up all on-disk state to a timestamped archive.          | `nexon backup-all`                                                       |
| `nexon restore <archive>`            | Restore DB and files from a backup archive (overwrites current).      | `nexon restore ~/.nexon/backups/...tar.gz`                               |
| `nexon backup-schedule`              | Show a cron line to schedule daily backups at 02:00 UTC.              | `nexon backup-schedule`                                                  |

---

## Notes

- Use `nexon <command> --help` for full flags and options.  
- All actions are logged in `~/.nexon/audit.log`, and audited via `/metrics` and Prometheus.  
- You can extend Nexon via **plugins**: drop them under `nexon_cli/plugins/` and enable in `~/.nexon/plugins.yaml`.  
- Example policies in `docs/policies.yaml.sample`, and scripts in `examples/` demonstrate end-to-end usage.  
- Refer to the **Getting Started** guide for a complete walk-through of core workflows.  
