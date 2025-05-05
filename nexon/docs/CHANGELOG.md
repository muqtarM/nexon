# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Placeholder for upcoming Enterprise & Integrations enhancements  
- More automation around multi-tenant SaaS deployment  

---

## [0.6.0] – 2025-05-05
### Added
- **High-Availability & DR**: `backup-all`, `restore`, and cron scheduling  
- **Integration Testing**: E2E GitHub Actions CI and `tests/test_integration.py`  
- **Further Reading** docs and examples consolidation  

---

## [0.5.0] – 2025-04-28
### Added
- **Kubernetes & Cloud Orchestration**: `cluster-deploy`, `cluster-expose`, `cluster-autoscale`  
- **Asset-Tracker Integration**: `shot-context`, `p4-sync`, and API `/assets` endpoints  
- **Telemetry**: background event queue, Segment/HTTP integration via hooks  

---

## [0.4.0] – 2025-04-20
### Added
- **Plugin Architecture** with `core/plugin_manager.py` and hook points  
- **Notifications & Webhooks** plugin (`nexon_cli/plugins/notify`) for Slack/Teams  
- **Shell & Completion** commands: `nexon shell`, `nexon completion`  
- **Release Automation**: `bump-version`, `build-release`, GitHub Actions `release.yml`  
- **Security & Compliance**: `security-scan`, policy-as-code engine, `policy-validate`/`policy-report`  
- **Monitoring & Metrics**: Prometheus `/metrics` for CLI and server  

---

## [0.3.0] – 2025-04-10
### Added
- **Web Dashboard & API** (FastAPI + D3 graph) under `nexon_web/`  
- **Render-Farm & CI** commands: `render-submit`, `ci-run`  
- **Layered Inheritance**: `create-layer`, `list-layers`, `show-effective`  
- **Env-file Export** for editor integration  

---

## [0.2.0] – 2025-03-25
### Added
- **Studio Must-Haves**: semantic version ranges, `--dry-run`, `diff-env`  
- **Wrap-Tool**: wrap arbitrary folders as packages  
- **RBAC & Audit Logging**: `roles.yaml`, `~/.nexon/audit.log`  

---

## [0.1.0] – 2025-03-01
### Added
- **Core Foundation**: `create-env`, `list-envs`, `activate-env`, `lock-env`  
- **Package Management**: `create-package`, `list-packages`, `install-package`, `build-package`  
- **Docker Export**: `build-docker`  
- **Dependency Solver** with semver support  

---
