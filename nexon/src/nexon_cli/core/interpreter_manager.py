import os
import sys
from pathlib import Path
from typing import Dict, Optional

from nexon_cli.utils.logger import logger
from nexon_cli.utils.file_ops import load_yaml
from nexon_cli.utils.paths import SETTINGS_PATH


class InterpreterManager:
    def __init__(self):
        self.default_python = sys.executable
        self.interpreter_map = self._load_interpreter_map()

    def _load_interpreter_map(self) -> Dict[str, str]:
        """
        Load interpreter mappings from the global settings file.
        :return:
        """
        if SETTINGS_PATH.exists():
            settings = load_yaml(SETTINGS_PATH)
            return settings.get("python_versions", {})
        else:
            logger.warning(f"No settings.yaml found at {SETTINGS_PATH}. Using system default interpreter")
            return {}

    def resolve_interpreter(self, package_list: list[str]) -> str:
        """
        Resolve the appropriate Python interpreter path based on the package list.
        :param package_list:
        :return:
        """
        for package in package_list:
            package_lower = package.lower()

            # Hardcoded matching for now, later this can be based on package metadata
            if "maya2023" in package_lower:
                return self.interpreter_map.get("maya2023", self.default_python)
            if "houdini19" in package_lower:
                return self.interpreter_map.get("houdini19", self.default_python)
            if "nuke14" in package_lower:
                return self.interpreter_map.get("nuke14", self.default_python)

        # Default if no special mapping method
        return self.default_python

    def print_current_interpreter(self):
        """
        Print the currently active Python interpreter info.
        :return:
        """
        logger.info(f"Current Interpreter: {sys.executable}")
        logger.info(f"Python Version: {sys.version}")

    def validate_interpreter(self, interpreter_path: str) -> bool:
        """
        Check if the interpreter path exists and is executable.
        :param interpreter_path:
        :return:
        """
        if not interpreter_path or not Path(interpreter_path).exists():
            logger.error(f"Interpreter not found: {interpreter_path}")
            return False
        return True

    def run_with_interpreter(self, interpreter_path: str, command_args: list[str]) -> int:
        """
        Execute a command with the specified interpreter (future use for launching apps/tools).
        :param interpreter_path:
        :param command_args:
        :return:
        """
        import subprocess

        if not self.validate_interpreter(interpreter_path):
            return 1

        full_command = [interpreter_path] + command_args
        logger.info(f"Running command: {' '.join(full_command)}")

        return subprocess.call(full_command)
