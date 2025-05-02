import yaml
from pathlib import Path


def save_yaml(path: Path, data: dict):
    """
    Save a dictionary to a YAML file
    :param path:
    :param data:
    :return:
    """
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


def load_yaml(path: Path) -> dict:
    """
    Load a dictionary from a YAML file
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
