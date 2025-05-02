# Nexon CLI Commands Reference

All commands are invoked via the `nexon` CLI.

---

## Phase 1 – Essential Foundation

| Command                   | Description                                                  | Example                                                   |
|---------------------------|--------------------------------------------------------------|-----------------------------------------------------------|
| `nexon create-env`        | Scaffold a new environment (creates `env.yaml`).             | `nexon create-env demo --role animator`                   |
| `nexon list-envs`         | List all existing environments.                              | `nexon list-envs`                                         |
| `nexon activate-env`      | Activate an environment (sets env-vars in your shell).       | `nexon activate-env demo`                                 |
| `nexon deactivate-env`    | Deactivate the current Nexon environment (restores shell).   | `nexon deactivate-env`                                    |
| `nexon lock-env`          | Freeze an environment to a lockfile (`env.lock.yaml`).       | `nexon lock-env demo`                                     |
| `nexon create-package`    | Scaffold a versioned package template.                       | `nexon create-package mytool --version 0.1.0`             |
| `nexon list-packages`     | List all packages and available versions.                    | `nexon list-packages`                                     |
| `nexon install-package`   | Install a package into an env (basic install).               | `nexon install-package demo mytool-0.1.0`                 |
| `nexon uninstall-package` | Remove a package-version from an environment.                | `nexon uninstall-package demo mytool-0.1.0`               |
| `nexon build-package`     | Run build steps (CMake, pip, custom) for a package.          | `nexon build-package mytool 0.1.0`                        |
| `nexon build-docker`      | Containerize an environment into a Docker image.             | `nexon build-docker demo --tag demo:latest`               |

---

## Phase 2 – Studio Must-Haves

| Command                                     | Description                                                       | Example                                                         |
|---------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------|
| `nexon install-package <env> <req> --dry-run` | Preview which packages *would* be added, without modifying env.    | `nexon install-package demo "mypkg>=1.2,<2.0" --dry-run`        |
| `nexon install-package <env> <range>`       | Install a semantic-version range of a package.                    | `nexon install-package demo "mypkg>=1.2,<2.0"`                  |
| `nexon diff-env <envA> <envB>`              | Show added/removed packages and role changes between two envs.    | `nexon diff-env dev staging`                                    |
| `nexon wrap-tool`                           | Wrap any folder as a Nexon package (auto-detects executables).    | `nexon wrap-tool /path/to/tool --name customtool --version 1.0`|

---

## Phase 3 – High-Impact Extensions

| Command                          | Description                                                              | Example                                                            |
|----------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------|
| `nexon render-submit`            | Build env into Docker and submit a render job to a farm (Deadline).      | `nexon render-submit vp_render /projects/shot01/scene_v001.mb`    |
| `nexon ci-run`                   | Build env into Docker and trigger a CI workflow (e.g. GitHub Actions).   | `nexon ci-run vp_ci_test tests/run_all.py`                        |

---

## Notes

- Flags such as `--farm`, `--options`, and `--runner` allow customization of render/CI integrations.  
- Use `nexon --help` or `nexon <command> --help` for full argument/option details.  
- RBAC and audit logging apply to all commands—see your `~/.nexon/roles.yaml` and `~/.nexon/audit.log` for user permissions and history.
