# Configuration Reference

Nexon and Nexon Server are driven entirely by environment variables and dot-env settings. This reference lists all supported settings, their defaults, and descriptions.

---

## CLI (`nexon_cli/core/config.py`)

| Variable            | Default             | Description                                                                                  |
|---------------------|---------------------|----------------------------------------------------------------------------------------------|
| `NEXON_BASE_DIR`    | `~/.nexon`          | Root directory for all Nexon state (envs, packages, layers, backups, plugins, audit.log).   |
| `DATABASE_URL`      | *required*          | SQLAlchemy database URL for the central server (or CLI if using SQLite).                     |
| `JWT_SECRET`        | *required*          | HMAC secret for signing JWT tokens (central server authentication).                          |
| `SHOTGRID_URL`      | `None`              | Base URL of your ShotGrid site (e.g. `https://studio.shotgrid.com`).                         |
| `SHOTGRID_SCRIPT`   | `None`              | ShotGrid API script name.                                                                    |
| `SHOTGRID_KEY`      | `None`              | ShotGrid API key for the script user.                                                        |
| `P4PORT`            | `None`              | Perforce server address (e.g. `perforce:1666`).                                              |
| `P4USER`            | `None`              | Perforce user.                                                                               |
| `P4CLIENT`          | `None`              | Perforce workspace/client name.                                                              |
| `TELEMETRY_ENABLED` | `false`             | If `true`, emits anonymized CLI events to `TELEMETRY_URL`.                                   |
| `TELEMETRY_URL`     | `None`              | HTTP endpoint (or Segment) to receive telemetry events.                                      |
| `TELEMETRY_API_KEY` | `None`              | API key or token for the telemetry endpoint.                                                 |

---

## Server (`app/config.py`)

| Variable                          | Default           | Description                                                                                     |
|-----------------------------------|-------------------|-------------------------------------------------------------------------------------------------|
| `DATABASE_URL`                    | *required*        | SQLAlchemy DB URL (Postgres, MySQL, SQLite, etc.).                                             |
| `JWT_SECRET`                      | *required*        | Secret used to sign/verify JWT access tokens.                                                  |
| `JWT_ALGORITHM`                   | `HS256`           | Algorithm for JWT (e.g. HS256, RS256).                                                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES`     | `60`              | Validity window for access tokens, in minutes.                                                 |
| `LDAP_URL`                        | `None`            | LDAP server URL for corporate Single Sign-On (optional).                                       |
| `LDAP_BASE_DN`                    | `None`            | Base DN for LDAP authentication.                                                                |
| `SSH_KEY_PATH`                    | `~/.ssh/id_rsa`   | (Optional) SSH key path for Git or Perforce integrations that require SSH.                      |
| `ALLOWED_ORIGINS`                 | `*`               | CORS allowed origins for the FastAPI server (comma-separated).                                  |
| `SHOTGRID_URL`                    | `None`            | ShotGrid site URL (for the asset-tracker integration in the server).                           |
| `SHOTGRID_SCRIPT`, `SHOTGRID_KEY` | `None`            | ShotGrid credentials (as in CLI).                                                               |
| `P4PORT`, `P4USER`, `P4CLIENT`    | `None`            | Perforce settings (as in CLI) for server-side asset sync.                                       |
| `PROMETHEUS_PATH`                 | `/metrics`        | HTTP path on which to expose Prometheus metrics.                                               |
| `POLICIES_PATH`                   | `~/.nexon/policies.yaml` | Filesystem path to your policy-as-code rules.                                         |

---

### Loading Order

1. **Environment Variables**  
2. **`.env` file** (in current working directory or project root)  
3. Defaults hard-coded into `BaseSettings` definitions  

Use `export VAR=...` or add to your `.env` to override.  

---

## Example `.env`

```ini
# Central Server
DATABASE_URL=postgresql://postgres:postgres@db.local:5432/nexon
JWT_SECRET=supersecretkey
ACCESS_TOKEN_EXPIRE_MINUTES=120
ALLOWED_ORIGINS=http://localhost:3000,https://studio.mycompany.com

# Asset Tracker
SHOTGRID_URL=https://studio.shotgrid.com
SHOTGRID_SCRIPT=my_script
SHOTGRID_KEY=abc123

# Perforce
P4PORT=perforce:1666
P4USER=jenkins
P4CLIENT=ci_ws

# Telemetry
TELEMETRY_ENABLED=true
TELEMETRY_URL=https://telemetry.mycompany.com/collect
TELEMETRY_API_KEY=tele_key_here
```