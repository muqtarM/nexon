# Acknowledgements

Nexon is the result of contributions from an amazing community of artists, engineers, and studios. Special thanks to:

- **Core Team**: Alice Smith, Bob Lee, Carol Nguyen  

[//]: # (- **Early Adopters**: Studio FX, Animatrix, VisionWorks  )
- **Plugin Authors**:  
  - notify (Slack & Teams webhooks)  
  - telemetry (Segment/Event API hooks)  
  - log_time (build timing logs)  

[//]: # (- **Beta Testers**: the SIGGRAPH 2025 demo group  )

---

# Support & Community

- **GitHub Issues**  
  Report bugs or request features at  
  <https://github.com/muqtarM/nexon/issues>

- **Discussions & Q&A**  
  Join the community on the “Discussions” tab:  
  <https://github.com/muqtarM/nexon/discussions>

- **Slack/Teams**  
  #nexon-general channel in your studio’s workspace  

- **Email**  
  muqtar.shaikh225@gmail.com  

[//]: # (- **Documentation**  )

[//]: # (  Hosted at <https://docs.yourcompany.com/nexon>  )

---

# Third-Party Dependencies

Nexon relies on a number of open-source libraries. Below is a non-exhaustive list:

| Package                   | Purpose                                        |
|---------------------------|------------------------------------------------|
| FastAPI                   | Web framework for the centralized server       |
| Typer                     | CLI framework                                 |
| SQLAlchemy                | ORM / database migrations via Alembic          |
| Alembic                   | Database schema migrations                    |
| Pydantic                  | Settings, schema validation                   |
| python-jose               | JWT token encoding/decoding                   |
| passlib[bcrypt]           | Password hashing                              |
| requests                  | HTTP requests for integrations                |
| prometheus-client         | Metrics exposition                            |
| click-completion          | Shell completion code generation               |
| kubernetes                | Kubernetes API client                         |
| Jinja2                    | HTML report templating                        |
| PyYAML                    | YAML parsing/dumping                          |
| packaging                 | Semantic version parsing                      |
| watchdog                  | (optional) FS‐watch for auto-reload features   |
| pg_dump / psql (system)   | Postgres backup & restore                     |

---

# Appendix: YAML Schemas

## Environment Definition (`.yaml`)

```yaml
# environments/<env_name>.yaml
name: <env_name>          # required
role: <role_name>         # required
packages:                 # list of package-version strings
  - pkgA-1.0.0
  - pkgB-2.1.0
env:                      # additional environment variables
  VAR1: value1
  PATH: "{root}/bin:{PATH}"
lockfile: <env_name>.lock.yaml  # optional, auto-generated
```

---
# Package Definition (`package.yaml`)
```yaml
name: <package_name>      # required
version: <semver>         # required
requires:                 # dependencies (semver exprs)
  - otherpkg>=2.0,<3.0
env:                      # env-vars injected on activation
  LIB_PATH: "{root}/lib"
build:                    # build recipe (CMake/pip/etc.)
  cmds:
    - mkdir build && cd build
    - cmake ..
    - make -j4
commands:                 # CLI‐exposed commands
  run: python -m mytool
license: MIT              # optional metadata
description: “…”          # optional
```

---
# End of Documentation
Thank you for exploring Nexon! For the latest updates, refer to the **Changelog** and subscribe to our release RSS feed.