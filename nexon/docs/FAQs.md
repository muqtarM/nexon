# FAQ & Troubleshooting

This section collects common questions, pitfalls, and how to resolve them.

---

## Q1: “I get `DATABASE_URL` validation errors when running Alembic.”

**Symptom:**  
```bash
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
DATABASE_URL …
```


**Solution:**  
- Create a `.env` in your project root with  
  ```ini
  DATABASE_URL=sqlite:///./nexon.db
  JWT_SECRET=devkey
  ```
- Or export them in your shell:
  ```bash
    export DATABASE_URL="sqlite:///./nexon.db"
    export JWT_SECRET="devkey"
  ```
- Then rerun `alembic upgrade head`.

---
## Q2: “`nexon shell <env>` fails with FileNotFoundError on Windows.”
**Symptom**:
```arduino
FileNotFoundError: [WinError 2] The system cannot find the file specified
```
**Cause**: Default `/bin/bash` is not on Windows PATH.

**Solution**:
- Explicitly pass a valid shell:
  ```bash
  nexon shell dev --shell "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
  ```
- Or rely on `%COMSPEC%`:
  ```bash
  nexon shell dev
  ```
  which uses `cmd.exe` or PowerShell.

---
## Q3: “`click_completion` errors: ‘dict’ object is not callable / no attribute `shells`.”
**Symptom**:

```pgsql
TypeError: 'dict' object is not callable
AttributeError: module 'click_completion.core' has no attribute 'shell_map'
```
**Solution**:
- Ensure you installed the correct package:
  ```bash
  pip install click-completion
  ```
- We updated `completion.py` to detect supported shells dynamically. Just rerun your command.
- If errors persist, verify `click_completion.core.shells()` exists in your version.

---
## Q4: “`from kubernetes.client import networking_v1` or `autoscaling_v1` not found.”
**Symptom**:

```pgsql
ImportError: cannot import name 'networking_v1' from 'kubernetes.client'
```
**Solution**:
- Use direct imports of API and model classes.
- Example for Ingress:
  ```python
  from kubernetes.client import NetworkingV1Api, V1Ingress, V1IngressSpec, V1ObjectMeta, …
  ```
- Example for HPA:
  ```python
  from kubernetes.client import AutoscalingV1Api, V1HorizontalPodAutoscaler, …
  ```
- See the **Kubernetes & Cloud Orchestration** section for complete import lists.

---
## Q5: “Metrics endpoint returns empty or missing counters.”
**Symptom**:
`HTTP GET /metrics` shows no `nexon_actions_total` gauge.

**Cause**:
- Audit log file `~/.nexon/audit.log` doesn’t exist or is empty.
- Or the server metrics router was not mounted.

**Solution**:
- Verify actions are logged:
  ```bash
  tail ~/.nexon/audit.log
  ```
- Ensure in `app/main.py` you have:
  ```python
  from app.routers.metrics import router as metrics_router
  app.include_router(metrics_router)
  ```
- Restart the server.

---
## 6. Common Pitfalls


|Issue	| Fix |
|-------|-----|
|`nexon` command not found after install	| Ensure your Python environment’s `bin/` is on PATH. |
| Permissions errors writing to `~/.nexon`	| Check file ownership or run `chmod -R u+rw ~/.nexon`.|
| Docker build errors (`Dockerfile` missing)|	Confirm `nexon build-docker` generated a valid `Dockerfile` in your project root.|
| Alembic can’t find `Base.metadata`	| Make sure `app/models/__init__.py` imports all models and exposes `Base`. |

---
# Architecture Overview
A high-level diagram of how the pieces fit together:

```pgsql
┌────────────┐   CLI   ┌────────────┐   HTTP   ┌────────────┐  
│   nexon    │ <─────> │  Core Lib  │ <──────> │  FastAPI   │  
│ (Typer App)│         │ (env/pkg/  │         │  Server &  │  
└────────────┘         │  cluster/  │         │  Dashboard │  
       │               │  policy/   │         └────────────┘  
       │ invoke        │  metrics)  │             
       ▼               └────────────┘             
 ┌───────────────┐                                
 │  Kubernetes   │                                
 │  Cluster /    │                                
 │  Cloud VMs    │                                
 └───────────────┘                                
       ▲                                        
       │ Telemetry /                               
       │ Asset/Perforce                            
       └─────────────────────────────────────────┐  
                                               │  
                                     ┌────────────────┐
                                     │  Prometheus /   │
                                     │  Grafana /      │
                                     │  Observability  │
                                     └────────────────┘
```
- **CLI** calls into the Core library for all operations (environments, packages, cluster, policies).
- **Core** drives subprocesses (Docker, p4, kubectl) and business logic.
- **FastAPI** server reuses Core to expose CRUD routes, metrics, and integrations.
- **Plugins** and **Telemetry** hook into Core events.
- **Prometheus** can scrape both CLI-exported metrics and server metrics for monitoring.

---
# Roadmap
Future areas of focus:
- **Multi-tenant SaaS**: central UI & project isolation
- **Enterprise SSO**: OAuth/OIDC, SAML integrations
- **Cloud VM orchestration**: Terraform & AWS/GCP/Azure modules
- **Enhanced UI**: React/Vue dashboard with live graphs
- **Policy marketplace**: shareable rule packs for compliance standards
- **Community plugins**: a registry of 3rd-party Nexon plugins

---
# License
```sql
MIT License

Copyright (c) 2025 Your Company

Permission is hereby granted, free of charge, to any person obtaining a copy
...
(full MIT text here)
```
