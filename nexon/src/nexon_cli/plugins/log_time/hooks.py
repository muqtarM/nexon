import time
from nexon_cli.utils.logger import logger


def pre_build_package(package: str, version: str):
    logger.info(f"[log_time] Starting build of {package}-{version} at {time.ctime()}")


def post_build_package(package: str, version: str):
    logger.info(f"[log_time] Finished build of {package}-{version} at {time.ctime()}")
