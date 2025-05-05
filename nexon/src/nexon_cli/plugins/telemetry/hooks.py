from nexon_cli.core.telemetry_manager import telemetry_manager


def post_create_env(env_name: str, role: str = None, **kwargs):
    telemetry_manager.send_event("create_env", {"env_name": env_name, "role": role})


def post_install_package(env_name: str, added: list, **kwargs):
    telemetry_manager.send_event("install_package", {"env_name": env_name, "packages": added})


def post_build_package(package: str, version: list, **kwargs):
    telemetry_manager.send_event("build_package", {"package": package, "version": version})
