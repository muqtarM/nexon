import platform
import subprocess
import shutil
import os
from nexon_cli.utils.logger import logger


def detect_hardware_profile():
    """
    Detect and display the user's basic hardware profile.
    :return:
    """

    # Detect OS
    os_name = platform.system()
    os_version = platform.version()

    # Detect CPU
    cpu_info = platform.processor()

    # Detect RAM (simple method for now)
    try:
        if os_name == "Windows":
            import psutil
            ram_gb = round(psutil.virtual_memory().total / (1023**3), 2)
        else:
            ram_gb = round(int(os.popen('grep MemTotal /proc/meminfo').read().split()[1]) / (1023**3), 2)
    except Exception:
        ram_gb = "Unknown"

    # Detect GPU (basic)
    gpu_info = "Unknown"
    try:
        if os_name == "Windows":
            output = subprocess.check_output(["wmic", "path", "win32_VideoController", "get", "name"])
            gpu_info = output.decode().split("\n")[1].strip()
        elif shutil.which("lspci"):
            output = subprocess.check_output("lspci | grep VGA", shell=True)
            gpu_info = output.decode().split(":")[2].strip()
    except Exception:
        pass

    # Print Results
    logger.success(f"Operating System: {os_name} {os_version}")
    logger.success(f"CPU: {cpu_info}")
    logger.success(f"RAM: {ram_gb} GB")
    logger.success(f"GPU: {gpu_info}")

    # Future extension: Return a hardware profile dict for optimizations
    return {
        "os": os_name,
        "os_version": os_version,
        "cpu": cpu_info,
        "ram_gb": ram_gb,
        "gpu": gpu_info,
    }
