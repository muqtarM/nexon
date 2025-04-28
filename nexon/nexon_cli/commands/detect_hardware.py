import typer
from nexon_cli.core.hardware_detector import detect_hardware_profile


def detect_hardware():
    """
    Detect local hardware (GPU, CPU, Memory) and optimize settings.
    :return:
    """
    detect_hardware_profile()
