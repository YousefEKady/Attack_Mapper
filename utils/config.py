import yaml
import os

def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"[!] Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError("[!] Config file is empty or invalid")
            return config
    except yaml.YAMLError as e:
        raise ValueError(f"[!] Error parsing YAML file: {e}")
