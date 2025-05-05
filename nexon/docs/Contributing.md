# Contributing

We welcome contributions of all kinds—from bug reports and documentation fixes to new features and plugins. Please follow these guidelines to help us review and merge your changes as smoothly as possible.

---

## 1. Get the Code

```bash
git clone https://github.com/MuqtarM/nexon.git
cd nexon
```

---
## 2. Set Up Your Development Environment
1. **Create a Python virtual environment** (recommended):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2. **Install development dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -e .[dev]
    ```
    
    This pulls in:
    - **FastAPI**, **Alembic**, **uvicorn** for the server
    - **pytest**, **Typer**, **click-completion**, **prometheus_client** for CLI and tests
    - **kubernetes**, **requests**, **Jinja2** for plugins and integrations


3. **Initialize the database** (SQLite by default):

    ```bash
    export DATABASE_URL="sqlite:///./nexon.db"
    alembic upgrade head
    ```
   
---
## 3. Run Tests
- **Unit & CLI tests**:

    ```bash
    pytest tests/test_layers.py tests/test_metrics.py tests/test_integration.py -q
    ```
- **API tests**:

    ```bash
    pytest tests/test_api_*.py -q
    ```
- **Lint & formatting**:

    ```bash
    black .        # auto‐format
    isort .        # sort imports
    flake8 .       # code quality checks
    ```

---
## 4. Coding Conventions
- **Python**: follow [PEP 8](https://peps.python.org/pep-0008/)
- **Imports**: grouped (stdlib, third-party, local), alphabetized by `isort`
- **Type hints**: use `typing` annotations liberally
- **Docstrings**: [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- **Commit messages**:
    ```bash
    feat(cli): add `nexon foo-bar` command
    fix(env): handle missing lockfile gracefully
    docs: update Getting Started guide
    test: add integration test for p4-sync
    ```
- **Branches**:
  - Prefix with `feat/`, `fix/`, `docs/`, `refactor/`, `ci/`
  - Target the `main` branch via PRs

---
## 5. Submitting a Pull Request
1. **Fork** the repository.
2. **Create** a feature branch:
    ```bash
    git checkout -b feat/my-cool-plugin
    ```
3. **Implement** your changes + tests.
4. **Run** all tests and linters locally.
5. **Push** your branch to your fork and **open** a PR against `main`.
6. **Fill out** the PR template with:
   - Summary of changes 
   - Motivation & context 
   - Screenshots or logs (if UI/UX changes)
   - Any follow-up tasks

---
## 6. Code of Conduct
This project follows the [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to abide by its terms.

---
## 7. Issues & Support
- **Bug reports & feature requests**: open an [issue](https://github.com/your-org/nexon/issues)
- **Discussion & Q&A**: use the “Discussions” tab
- **Chat**: join our Slack channel `#nexon` for live help

Thank you for helping make Nexon even better! 🚀