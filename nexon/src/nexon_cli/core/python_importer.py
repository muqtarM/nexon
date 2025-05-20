import subprocess
import tempfile
import shutil
import wheel_inspect
import yaml
import tarfile
from pathlib import Path

from nexon_cli.utils.logger import logger
from nexon_cli.core.configs import config


class PythonImporterError(Exception):
    pass


class PythonPackageImporter:
    """
    Download a package (wheel or sdist) from PyPI or local path,
    inspect metadata (including Required-Dict), scaffold Nexon packages,
    and optionally import dependencies as Nexon packages too.
    """

    def import_from_pypi(self,
                         requirement: str,
                         index_url: str | None = None,
                         extra_index_url: str | None = None,
                         include_deps: bool = False
                         ) -> list[str]:
        """
        Download & import a PyPI package and (optionally) its Requires-Dist dependencies.
        Returns a list of all imported 'name-version' strings.
        """
        imported = []

        def _rec_import(req: str):
            if req in seen:
                return
            seen.add(req)

            # 1) Download without deps
            with tempfile.TemporaryDirectory() as td:
                cmd = ["pip", "download", "--no-deps", "--dest", td, req]
                if index_url:
                    cmd += ["--index-url", index_url]
                if extra_index_url:
                    cmd += ["--extra-index-url", extra_index_url]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    raise PythonImporterError(f"pip download failed for {req}: {e.stderr.decode()}")

                # 2) Find the wheel or sdist
                files = list(Path(td).glob("*.whl")) or list(Path(td).glob("*.tar.gz"))
                if not files:
                    raise PythonImporterError(f"No wheel or sdist found for {req}")
                dist_path = files[0]

                # 3) Inspect metadata
                name, version, requires = self._inspect_metadata(dist_path)

                pkgver = f"{name}-{version}"
                if pkgver in imported:
                    return
                imported.append(pkgver)

                # 4) Scaffold package directory
                pkg_dir = Path(config.packages_dir) / name / version
                pkg_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(dist_path, pkg_dir / dist_path.name)

                # 5) Write package.yaml with requires from metadata
                pkg_yaml = {
                    "name": name,
                    "version": version,
                    "requires": requires,
                    "env": {},
                    "build": {},
                    "commands": {}
                }
                (pkg_dir / "package.yaml").write_text(
                    yaml.safe_dump(pkg_yaml), encoding="utf-8"
                )

            # 6) Recurse into dependencies
            if include_deps:
                for dep in requires:
                    _rec_import(dep)

        seen = set()
        _rec_import(requirement)
        return imported

    def import_from_file(self,
                         dist_path: Path,
                         include_deps: bool = False
                         ) -> list[str]:
        """
        Inspect a local .whl or .tar.gz, scaffold the Nexon package,
        and optionally import Requires-Dist dependencies.
        """
        imported = []

        def _rec_file(path: Path):
            name, version, requires = self._inspect_metadata(path)
            pkgver = f"{name}-{version}"
            if pkgver in imported:
                return
            imported.append(pkgver)

            pkg_dir = Path(config.packages_dir) / name / version
            pkg_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(path, pkg_dir / path.name)
            pkg_yaml = {
                "name": name,
                "version": version,
                "requires": requires,
                "env": {},
                "build": {},
                "commands": {}
            }
            (pkg_dir / "package.yaml").write_text(
                yaml.safe_dump(pkg_yaml), encoding="utf-8"
            )
            logger.success(f"Imported {pkgver} from file (requires: {requires})")

            if include_deps:
                for dep in requires:
                    # delegate to import_from_pypi for remote deps
                    self.import_from_pypi(dep, include_deps=True)

        _rec_file(dist_path)
        return imported

    def _inspect_metadata(self, dist_path: Path) -> tuple[str, str, list[str]]:
        """
        Returns (name, version, requires_list) by inspecting wheel or PKG-INFO.
        """
        requires = []
        if dist_path.suffix == ".whl":
            info = wheel_inspect.inspect_wheel(dist_path)
            print("info", info['dist_info']["metadata"].keys())
            name = info['dist_info']["metadata"]["name"]
            version = info['dist_info']["metadata"]["version"]
            requires = info['dist_info']["metadata"].get("requires_dist", []) or []
        else:
            # sdist: extract PKG-INFO
            with tarfile.open(dist_path) as tar:
                members = [m for m in tar.getmembers() if m.name.endswith("PKG-INFO")]
                if not members:
                    raise PythonImporterError("No PKG-INFO in sdist")
                f = tar.extractfile(members[0])
                content = f.read().decode()
            meta = {}
            for line in content.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key == "Requires-Dist":
                        requires.append(val)
                    else:
                        meta.setdefault(key, val)
            name = meta.get("Name")
            version = meta.get("Version")
            if not name or not version:
                raise PythonImporterError("Failed to parse Name/Version from PKG-INFO")

        # Normalize requires strings (PEP 508)
        return name, version, requires
