import yaml, json, pathlib, sys
from pathlib import Path
cfg_path = pathlib.Path(__file__).resolve().parent / "config" / "settings.yaml"
print(cfg_path)
print(PROJECT_ROOT:= Path(__file__).resolve().parent)
