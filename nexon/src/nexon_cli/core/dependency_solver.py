import re
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.requirements import Requirement, InvalidRequirement

from nexon_cli.utils.logger import logger
from nexon_cli.utils.file_ops import load_yaml
from nexon_cli.utils.paths import PACKAGES_DIR


class DependencyError(Exception):
    """Custom exception for dependency resolution errors."""
    pass


class DependencySolver:
    """
    Resolve package dependencies, including semantic version ranges, and detect conflicts.
    """
    def __init__(self):
        self.packages_dir = PACKAGES_DIR
        self._definitions: dict[str, dict[str, dict]] = {}

    def _load_definitions(self) -> dict[str, dict[str, dict]]:
        """Load all package specs from PACKAGES_DIR."""
        if self._definitions:
            return self._definitions

        defs: dict[str, dict[str, dict]] = {}
        for pkg_dir in self.packages_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            name = pkg_dir.name
            defs[name] = {}
            for ver_dir in pkg_dir.iterdir():
                if not ver_dir.is_dir():
                    continue
                pkg_file = ver_dir / "package.yaml"
                if not pkg_file.exists():
                    continue
                data = load_yaml(pkg_file)
                vers = data.get("version")
                if not vers:
                    logger.warning(f"No version field in {pkg_file}, skipping.")
                    continue
                defs[name][vers] = data

        self._definitions = defs
        return defs

    def parse_requirement(self, req: str):
        """
        Parse requirement specifier into package name and version constraint.
        Supports:
            - Exact: 'mypkg-1.2.3'
            - Range: 'mypkg>=1.2,<2.0',
            - Implicit latest: 'mypkg'
        Returns (name, constraint) where constraint is None or e.g. '>=1.2,<2.0' or '==1.2.3'
        :param req:
        :return:
        """
        exact = re.match(r"^([A-Za-z0-9_.]+)-(\d+(?:\.\d+)*)$", req)
        if exact:
            # Exact version shorthand: foo-1.2.3
            name, vers = exact.group(1), exact.group(2)
            try:
                Version(vers)
            except InvalidVersion:
                raise DependencyError(f"Invalid version in exact requirement: {req}")
            return name, SpecifierSet(f"=={vers}")

        # # 2) PEP 508 / packaging.Requirement
        # try:
        #     requirement = Requirement(req)
        # except InvalidRequirement as e:
        #     raise DependencyError(f"Invalid requirement '{req}': {e}")
        # return requirement.name, requirement.specifier

        # 2) Range spec: find first operator position
        ops = ["==", ">=", "<=", "~=", "!=", ">", "<"]
        pos = len(req)
        for op in ops:
            idx = req.find(op)
            if idx != -1 and idx < pos:
                pos = idx
        if pos < len(req):
            name = req[:pos]
            spec = req[pos:]
            try:
                spec_set = SpecifierSet(spec)
            except InvalidSpecifier as e:
                raise DependencyError(f"Invalid version specifier '{spec}' in '{req}': {e}")
            return name, spec_set

        # 3) No version part
        return req, SpecifierSet()

    def list_versions(self, name: str) -> List[Version]:
        """
        List all sort available versions from the cached definitions.
        :param name:
        :return:
        """
        defs = self._load_definitions()
        if name not in defs:
            raise DependencyError(f"Package '{name}' not found")
        versions = []
        for ver_str in defs[name]:
            try:
                versions.append(Version(ver_str))
            except InvalidVersion:
                logger.warning(f"Ignoring invalid version '{ver_str}' for package '{name}'")
        return sorted(versions, reverse=True)

    def resolve(self, req: str) -> str:
        """
        Resolve a list of requirements into exact versions, handling ranges.
        Returns list of 'pkg-version'. Raises on conflict or missing.
        :param req:
        :return:
        """
        name, spec = self.parse_requirement(req)
        # available = self.list_versions(name)
        # for v in available:
        #     if v in spec:
        #         return f"{name}-{v}"
        # # No match found
        # raise DependencyError(f"No version of '{name}' matches specifier '{spec}'")
        defs = self._load_definitions()

        if name not in defs:
            raise DependencyError(f"Package '{name}' not found")

        # Gather and sort all available versions
        available = []
        for vers_str in defs[name]:
            try:
                available.append(Version(vers_str))
            except InvalidVersion:
                logger.warning(f"Ignoring invalid version '{vers_str}' for '{name}'")
        available.sort(reverse=True)

        # Pick the first one that satisfies
        for v in available:
            if v in spec:
                return f"{name}-{v}"
        raise DependencyError(f"No version of '{name}' matches specifier '{spec}'")

    def resolve_all(self, requirements: list[str]) -> list[str]:
        """
        Resolve multiple requirements (including transitive 'requires') into
        a flat list of exact package-version strings.
        :param requirements:
        :return:
        """
        defs = self._load_definitions()
        resolved = set()
        to_process = list(requirements)

        while to_process:
            req = to_process.pop(0)
            pkgver = self.resolve(req)
            if pkgver in resolved:
                continue
            resolved.add(pkgver)

            # Load that package's own requires
            name, vers = pkgver.split("-", 1)
            meta = defs[name].get(vers)
            for dep in meta.get("requires", []):
                # Only enqueue if we haven't already resolved it
                if self.resolve(dep) not in resolved:
                    to_process.append(dep)

        # Return sorted for consistency
        return sorted(resolved)

    def build_graph(self, requirements: List[str]) -> Dict[str, List[str]]:
        """
        Build a dependency DAG given top-level requirements. Each package spec may have 'requires'.
        Returns adjacency list: {'pkg-ver': ['dep1-ver', ...]}
        :param requirements:
        :return:
        """
        defs = self._load_definitions()
        graph: Dict[str, List[str]] = {}
        queue = list(requirements)

        while queue:
            req = queue.pop(0)
            pkgver = self.resolve(req)
            if pkgver in graph:
                continue

            name, vers = pkgver.split("-", 1)
            meta = defs[name][vers]
            direct = meta.get("requires", [])

            # Resolve direct dependencies to exact versions
            resolved_direct = []
            for dep in direct:
                dep_pkgver = self.resolve(dep)
                resolved_direct.append(dep_pkgver)
                queue.append(dep)  # ensure we process dependencies of dependencies

            graph[pkgver] = resolved_direct

        return graph
