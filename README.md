# Nexon Quickstart

**Nexon** is a next-generation multimedia environment manager for VFX, Games, Virtual Production, XR, AI, and more.

---

## Installation

1. **Clone the repository** or install via pip (if published):

   ```bash
   git clone https://github.com/your-org/nexon.git
   cd nexon
   ```

2. **Install dependencies** (Python 3.12+ recommended):

   ```bash
   pip install -e .
   ```

3. **Verify CLI**:

   ```bash
   nexon --help
   ```

---

## Create an Environment

1. **Create** a new environment named `demo` (role: animator):

   ```bash
   nexon create-env demo --role animator
   ```

2. **List** available environments:

   ```bash
   nexon list-envs
   ```

3. **Activate** the `demo` environment:

   ```bash
   nexon activate-env demo
   ```

   > This sets `NEXON_ENV`, merges any package-`env` variables, and selects the appropriate Python interpreter.

4. **Deactivate** when done:

   ```bash
   nexon deactivate-env
   ```

---

## Scaffold & Install a Package

1. **Scaffold** a new tool package `mytool` version `0.1.0`:

   ```bash
   nexon create-package mytool 0.1.0
   ```

2. **Edit** the generated file at:

   ```text
   ~/.nexon/packages/mytool/0.1.0/package.yaml
   ```

   Add your metadata, dependencies, `env` vars, and optional `build` commands. Example:

   ```yaml
   name: mytool
   version: 0.1.0
   description: "Example Python tool"
   requires: []
   env:
     PATH: "{root}/bin:{PATH}"
     PYTHONPATH: "{root}/src:{PYTHONPATH}"
   build:
     commands:
       - cd {root}/src && pip install .
   ```

3. **Install** into the `demo` environment (auto-resolves dependencies):

   ```bash
   nexon install-package demo mytool
   ```

4. **Verify** installed packages:

   ```bash
   nexon list-packages
   ```

---

## Lock & Export

1. **Lock** the `demo` environment (for reproducibility):

   ```bash
   nexon lock-env demo
   ```

   > Creates `~/.nexon/environments/demo.lock.yaml` capturing exact package versions.

2. **Build** a Docker image for `demo`:

   ```bash
   nexon build-docker demo --tag myorg/demo:1.0
   ```

   > Generates a `Dockerfile` in `~/.nexon/dockerfiles/demo/`, then runs `docker build`.

---

## Examples Directory

```
examples/
├── env_animator.yaml       # Sample animator env spec
├── package_mytool.yaml     # Sample package.yaml for a Python tool
└── recipe_override.yaml    # Sample recipe to override base env
```

Use these as starting points to build your own specs.

---

For more commands and advanced features (workspaces, recipes, hardware detection), see the full documentation at `docs/` or run:

```bash
nexon COMMAND --help
```

---

## Render-Farm Submission

Build your environment into Docker and submit a render job:

```bash
# Build Docker image and submit to Deadline render farm
nexon render-submit <env_name> <scene_file.mb> \
  [--farm deadline] \
  [--options "-Priority 75 -Comment \"Automated submit\""]
```

- `<env_name>`: name of the Nexon environment (e.g. `vp_render`)

- `<scene_file.mb>`: path to your scene file (e.g. Maya `.mb`)

- `--farm`: which render farm CLI to use (default: `deadline`)

- `--options`: any additional flags passed directly to the farm CLI

---

## CI Job Trigger
Package your environment and trigger a CI workflow (e.g. GitHub Actions):

```bash
# Build Docker image and trigger a GitHub Actions workflow
nexon ci-run <env_name> <script_path> \
  [--runner github-actions]
```

- `<env_name>`: name of the Nexon environment (e.g. `ci_test`)

- `<script_path>`: path to the CI script or test harness (e.g. `tests/run_all.py`)

- `--runner`: identifier of the CI runner or workflow (default: `github-actions`)

---

## Sample `roles.yaml`
To enforce RBAC, place a `roles.yaml` under your Nexon base directory (`~/.nexon/roles.yaml`):
```yaml
# ~/.nexon/roles.yaml
users:
  alice: admin
  bob: dev
  carol: artist
```

Only users in the allowed roles can perform sensitive actions (e.g. create-package, render-submit).

---

## Example Audit Log
Every action is recorded in `~/.nexon/audit.log` with timestamp, user, action, target, and details:

```makefile
2025-05-02T15:04:22 | alice      | create_env     | vp_render            | role=artist
2025-05-02T15:05:10 | bob        | install_package| vp_render            | requirement=houdini>=19.0
2025-05-02T15:10:37 | alice      | render_submit  | vp_render            | scene=scene01.mb
2025-05-02T15:12:05 | carol      | ci_run         | vp_ci_test           | script=test_suite.py
```

---

## Next Steps
See [docs/commands.md](nexon/docs/commands.md) for a full CLI reference, grouped by project phase.
