import yaml
from pathlib import Path
from typing import Any, Dict, List
from jinja2 import Environment, PackageLoader, select_autoescape

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger
from nexon_cli.core.security_manager import SecurityManager
from nexon_cli.core.dependency_solver import DependencySolver


class PolicyError(Exception):
    pass


class PolicyManager:
    """
    Loads policy-as-code rules and applies them against environments.
    Supports:
        - Disallowed packages/licenses (from SecurityManager)
        - Minimum versions, allowed ranges
        - Custom YAML/XPath-like assertions on env metadata
    """

    def __init__(self):
        self.path = Path(config.base_dir) / "policies.yaml"
        if not self.path.exists():
            raise PolicyError(f"No policy file at {self.path}")
        self.rules = yaml.safe_load(open(self.path, "r"))

    def validate(self, env_name: str) -> List[Dict[str, Any]]:
        """
        Validate all rules against the given environment.
        Returns a list of violation dicts:
            {rule_id, description, details}
        """
        violations = []

        # 1) reuse SecurityManager for license/vuln/pkg-name rules
        sm = SecurityManager()
        sec_issues = sm.scan_environment(env_name)
        for issue in sec_issues:
            violations.append({
                "rule_id": "security",
                "description": issue,
                "details": {}
            })

        # 2) Min-version rules
        for rv in self.rules.get("min_versions", []):
            name = rv["package"]
            minv = rv["version"]
            solver = DependencySolver()
            try:
                resolved = solver.resolve(f"{name}>={minv}")
            except Exception:
                violations.append({
                    "rule_id": f"min_version:{name}",
                    "description": f"{name} < {minv}",
                    "details": {}
                })

        # 3) Arbitrary assertions on env fields
        env_data = __import__("nexon_cli.core.env_manager", fromlist=["EnvironmentManager"]) \
            .EnvironmentManager().get_environment(env_name)
        for assertion in self.rules.get("asset", []):
            # each rule: id, path (dot...), op, value
            field = assertion["path"]
            op = assertion["op"]
            val = assertion["value"]
            # Simple dot-traverse
            parts = field.split(".")
            cur = env_data
            for p in parts:
                cur = cur.get(p, None) if isinstance(cur, dict) else None
            ok = False
            if op == "eq":
                ok = (cur == val)
            elif op == "ne":
                ok = (cur != val)
            elif op == "in":
                ok = (cur in val)
            elif op == "regex":
                import re
                ok = bool(re.match(val, str(cur)))
            if not ok:
                violations.append({
                    "rule_id": assertion["id"],
                    "description": assertion.get("desc", f"{field} {op} {val}"),
                    "details": {"found": cur}
                })

        return violations

    def render_report(self, env_name: str, violations: List[Dict], out_path: Path):
        """
        Render an HTML compliance report using Jinja2 templates.
        """
        j2 = Environment(
            loader=PackageLoader("nexon_cli", "templates"),
            autoescape=select_autoescape(["html"])
        )
        tp1 = j2.get_template("policy_report.html")
        html = tp1.render(env=env_name, violations=violations)
        out_path.write_text(html, encoding="utf-8")
        logger.success(f"Wrote policy report to {out_path}")
