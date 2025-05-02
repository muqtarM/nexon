import yaml
import requests
from pathlib import Path
from typing import List, Dict

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger


class SecurityError(Exception):
    """
    Raised on security or policy violations.
    """


class SecurityManager:
    """
    Scans environments and packages for policy violations and known vulnerabilities
    """

    def __init__(self):
        self.policies_file = Path(config.base_dir) / "policies.yaml"
        self.policies = self._load_policies()

    def _load_policies(self) -> dict:
        if not self.policies_file.exists():
            logger.warning(f"No policies file at {self.policies_file}, using empty defaults")
            return {}
        return yaml.safe_load(open(self.policies_file, "r")) or {}

    def _get_vulns(self, name: str, version: str) -> List[Dict]:
        """
        Query OSV API for vulnerabilities in the given PYPI package version.
        """
        url = "https://api.osv.dev/v1/query"
        payload = {"version": version, "package": {"name": name, "ecosystem": "PyPI"}}
        try:
            resp = requests.post(url, json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            return data.get("vulns", [])
        except Exception as e:
            logger.error(f"OSV query failed for {name}-{version}: {e}")
            return []

    def scan_environment(self, env_name: str) -> List[str]:
        """
        Scan all packages in the environment for policy and vulnerability issues.
        Returns a list of human-readable issue strings.
        """
        from nexon_cli.core.env_manager import EnvironmentManager
        from nexon_cli.core.package_manager import PackageManager

        issues: List[str] = []

        # Load environment
        em = EnvironmentManager()
        env_data = em.get_environment(env_name)
        pkg_list = env_data.get("packages", [])

        # Policies
        dis_licenses = set(self.policies.get("disallowed_licenses", []))
        dis_pkgs = set(self.policies.get("disallowed_packages", []))

        pm = PackageManager()

        for pkgver in pkg_list:
            try:
                name, version = pkgver.split("-", 1)
            except ValueError:
                issues.append(f"Malformed package entry '{pkgver}'")
                continue

            # Policy: disallowed packages
            if name in dis_pkgs:
                issues.append(f"Package '{name}' is disallowed by policy")

            # Policy: license_cjeck
            pkg_file = Path(config.packages_dir) / name / version / "package.yaml"
            if pkg_file.exists():
                spec = yaml.safe_load(pkg_file.read_text())
                lic = spec.get("license")
                if lic and lic in dis_licenses:
                    issues.append(f"{pkgver} uses disallowes license '{lic}'")
            else:
                issues.append(f"Metadata for {pkgver} missing, cannot check license")

            # Vulnerability scan
            vulns = self._get_vulns(name, version)
            for v in vulns:
                summary = v.get("summary", "no summary")
                issues.append(f"{pkgver} has vulnerability {v['id']}: {summary}")

        return issues

    def scan_package(self, name: str, version: str) -> List[str]:
        """
        Scan a single package for policy and vulnerability issues.
        """
        return self.scan_environment_for_list([f"{name}-{version}"])

    def scan_environment_for_list(self, pkg_list: List[str]) -> List[str]:
        """
        Helper to scan an arbitary list of package-version strings.
        """
        issues: List[str] = []
        # reuse scan logic by creating a dummy env file in memory
        from nexon_cli.core.env_manager import EnvironmentManager
        em = EnvironmentManager()
        # Monkeypatch get_environment to return our list
        original = em.get_environment
        em.get_environment = lambda _: {"packages": pkg_list}
        try:
            issues = self.scan_environment("dummy")
        finally:
            em.get_environment = original
        return issues
