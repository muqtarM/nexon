# Plugin Development Guide

Nexon’s plugin architecture lets you extend nearly every action without touching core code. This guide shows you how to write, enable, and debug your own plugins.

---

## 1. How Plugins Work

1. **Hook points** are registered when Nexon starts.  
2. **`plugins.yaml`** lists which plugins to load.  
3. For each hook point, Nexon will call into your plugin’s function with named arguments.  

---

## 2. Available Hook Points

| Hook name               | When it fires                                           | Sample signature                              |
|-------------------------|---------------------------------------------------------|-----------------------------------------------|
| `pre_create_env`        | Before creating a new environment                       | `def pre_create_env(env_name: str, role: str)`|
| `post_create_env`       | After environment YAML is written                       | `def post_create_env(env_name: str, role: str)`|
| `pre_install_package`   | Before resolving & installing a package                 | `def pre_install_package(env_name: str, requirement: str)`|
| `post_install_package`  | After package(s) added to an environment                | `def post_install_package(env_name: str, added: list[str])`|
| `pre_build_package`     | Before running build steps for a package                | `def pre_build_package(package: str, version: str)`|
| `post_build_package`    | After package build completes                           | `def post_build_package(package: str, version: str)`|
| `pre_activate_env`      | Before setting shell variables on `activate-env`        | `def pre_activate_env(env_name: str)`         |
| `post_activate_env`     | After the shell variables have been exported            | `def post_activate_env(env_name: str)`        |
| `render_submit`         | After a render-submit call                              | `def render_submit(env_name: str, scene_file: str)`|
| `ci_run`                | After a ci-run call                                     | `def ci_run(env_name: str, script: str)`      |
| *(…and more; see source `HOOK_POINTS` in `core/plugin_manager.py`)* |  |  |

---

## 3. Plugin Directory Layout

Create a folder under `nexon_cli/plugins/` with this structure:
```folder
nexon_cli/
└── plugins/
└── my_plugin/
├── init.py
└── hooks.py
```


---

## 4. Writing Your First Plugin

### 4.1 `hooks.py` Example

```python
# nexon_cli/plugins/my_plugin/hooks.py

from nexon_cli.utils.logger import logger

def post_create_env(env_name: str, role: str = None, **kwargs):
    logger.info(f"[my_plugin] New env created: {env_name} (role={role})")

def pre_install_package(env_name: str, requirement: str, **kwargs):
    logger.debug(f"[my_plugin] Installing {requirement} into {env_name}")
```

 - Any hook gets passed only the named parameters it declares.

 - `**kwargs` catches extra data so your plugin won’t error if Nexon adds new fields.

### 4.2 Optional Dependencies
If your plugin needs extra libraries, list them in your studio’s documentation and ensure users install them, e.g.:

```bash
pip install nexon[my-plugin]
```
You can also catch `ImportError` in `hooks.py` to disable features gracefully.

---

## 5. Enabling Plugins
Create or update `~/.nexon/plugins.yaml`:

```yaml
# ~/.nexon/plugins.yaml
plugins:
  - my_plugin
  - notify
  - telemetry
```
Nexon will:
 1. Import `nexon_cli.plugins.my_plugin.hooks`
 2. Scan for any of the `HOOK_POINTS` functions 
 3. Register them under the matching hook

---

## 6. Debugging
 - Enable debug logging:
```bash
export NEXON_LOG_LEVEL=DEBUG
```

 - Check console for messages like:
```pgsql
DEBUG Registered hook post_create_env from my_plugin
DEBUG [my_plugin] New env created: demo
```

 - If your plugin fails to import, Nexon logs an error and continues loading others.

---
## 7. Advanced Topics
- **Conditional hooks**: inspect `config` or environment to no-op in certain contexts. 
- **Asynchronous work**: spin off background threads or enqueue tasks (e.g. webhook retries). 
- **Shared utilities**: put common helper code under `nexon_cli/plugins/my_plugin/lib/` and import in hooks.

---
## 8. Summary
1. Create `plugins/<your_plugin>/hooks.py`
2. Implement any subset of the official hook point functions 
3. Enable in `~/.nexon/plugins.yaml`
4. Test by running the matching Nexon command and watching the logs

Now go forth and make Nexon do exactly what your studio needs—without ever modifying core code!
