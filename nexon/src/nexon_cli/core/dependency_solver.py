import re
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

from packaging import version as pkg_version

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
        self.pkg_defs: Dict[str, List[str]] = {}  # name -> list of available versions (sorted)
        self._load_definitions()

    def _load_definitions(self):
        """Load all package specs from PACKAGES_DIR."""
        base = PACKAGES_DIR
        if not base.exists():
            logger.warning(f"Packages directory not found: {base}")
            return

        for pkg_dir in base.iterdir():
            if not pkg_dir.is_dir():
                continue
            name = pkg_dir.name
            versions = []
            for ver_dir in pkg_dir.iterdir():
                pkg_file = ver_dir / "package.yaml"
                if pkg_file.exists():
                    try:
                        data = load_yaml(pkg_file)
                        ver = data.get("version")
                        if ver:
                            versions.append(ver)
                    except Exception as e:
                        logger.warning(f"Failed to load {pkg_file}: {e}")
            # Sort descending
            try:
                sorted_versions = sorted(
                    versions,
                    key=lambda v: pkg_version.parse(v),
                    reverse=True
                )
                self.pkg_defs[name] = sorted_versions
            except Exception as e:
                logger.error(f"Error sorting versions for {name}: {e}")

    def parse_requirement(self, req: str) -> Tuple[str, Optional[str]]:
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
        # Range spec: look for comparison operators
        m = re.match(r"^([a-zA-Z0-9_\-]+)([><=!].+)$", req)
        if m:
            name, constraint = m.group(1), m.group(2)
            return name, constraint
        # Exact version with dash
        if '-' in req:
            parts = req.rsplit('-', 1)
            if len(parts) == 2 and re.match(r"^\d+\.\d+.*", parts[1]):
                return parts[0], f"=={parts[1]}"
        # No spec
        return req, None

    def resolve(self, requirements: list[str]) -> list[str]:
        """
        Resolve a list of requirements into exact versions, handling ranges.
        Returns list of 'pkg-version'. Raises on conflict or missing.
        :param requirements:
        :return:
        """
        resolved = {}
        for req in requirements:
            name, constraint = self.parse_requirement(req)
            if name not in self.pkg_defs:
                msg = f"Unknown package '{name}'"
                logger.error(msg)
                raise DependencyError(msg)
            candidates = self.pkg_defs[name]
            if not candidates:
                msg = f"No versions available for '{name}'"
                logger.error(msg)
                raise DependencyError(msg)

            chosen = None
            if constraint:
                # Evaluate each candidate against the constraint
                for ver in candidates:
                    expr = f"pkg_version.parse('{ver}'){constraint}"
                    try:
                        if eval(expr):  # constraint like '>=1.2,<2.0'
                            chosen = ver
                            break
                    except Exception:
                        continue
                if not chosen:
                    msg = f"No versions of '{name}' match '{constraint}'"
                    logger.error(msg)
                    raise DependencyError(msg)
            else:
                # No constraint: pick latest
                chosen = candidates[0]

            # Check for conflicts
            if name in resolved and resolved[name] != chosen:
                msg = f"Version conflict for '{name}': {resolved[name]} vs {chosen}"
                logger.error(msg)
                raise DependencyError(msg)

            resolved[name] = chosen

        # Build list of 'name-version'
        return [f"{n}-{v}" for n, v in resolved.items()]

    def build_graph(self, requirements: List[str]) -> Dict[str, List[str]]:
        """
        Build a dependency DAG given top-level requirements. Each package spec may have 'requires'.
        Returns adjacency list: {'pkg-ver': ['dep1-ver', ...]}
        :param requirements:
        :return:
        """
        topo_graph: Dict[str, List[str]] = defaultdict(list)
        queue = deque()
        visited = set()

        # Resolve initial requirements
        try:
            initial = self.resolve(requirements)
        except DependencyError as e:
            raise

        for pkgver in initial:
            queue.append(pkgver)

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            name, ver = node.rsplit('-', 1)
            pkg_file = PACKAGES_DIR / name / ver / "package.yaml"
            if not pkg_file.exists():
                logger.warning(f"Missing spec for '{node}' at {pkg_file}")
                continue
            data = load_yaml(pkg_file)
            deps = data.get("requires", [])
            try:
                child_nodes = self.resolve(deps)
            except DependencyError as e:
                logger.error(f"Failed to resolve children of '{node}': {e}")
                raise
            topo_graph[node] = child_nodes
            for child in child_nodes:
                if child not in visited:
                    queue.append(child)

        return dict(topo_graph)
