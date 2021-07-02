# std
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, Union

# lib
import yaml


class Mode(Enum):
    CONSECUTIVE = 1
    ITERATIVE = 2


class Config:
    def __init__(self, config_path: Path):
        if not config_path.is_file():
            raise ValueError(f"Invalid config.yaml path: {config_path}")

        with open(config_path, "r", encoding="UTF-8") as config_file:
            self._raw = yaml.safe_load(config_file)

        #self._get_mode()

    def get(self, key: str, required: bool = True) -> Optional[Union[str, list, int, bool]]:
        if key not in self._raw.keys():
            if required:
                raise ValueError(f"Invalid config - cannot find {key} key")
            else:
                return None

        return self._raw[key]
    
    @property
    def threshold(self):
        return self._raw.get('threshold') * 1073741824
    
    @property
    def raw(self):
        return self._raw

    #def _get_mode(self):
    #    self.mode = Mode(self._config.get('mode'))


def check_keys(required_keys, config) -> bool:
    for key in required_keys:
        if key not in config.keys():
            logging.error(f"Incompatible configuration. Missing {key} in {config}.")
            return False
    return True


def is_windows() -> bool:
    return sys.platform.startswith("win")
