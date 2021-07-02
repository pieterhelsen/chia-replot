import logging
import re
import shutil
from datetime import datetime
from abc import ABC
from pathlib import Path
from time import sleep
from typing import Optional

from src.config import Config


class PathManager(ABC):

    def __init__(self, config: Config):
        self._config = config
        self._paths = self._config.raw.get('paths')
        self._current_path = Path(self._paths.pop(0))
        self._date = datetime.strptime(self._config.raw.get('date'), '%Y/%m/%d %H:%M:%S')

        logging.info(f"Setting up chia-replot to delete plots older than {self._date.strftime('%Y/%m/%d %H:%M')}")

    def start_loop(self):
        interval = self._config.get('interval')

        while True:
            self.clear(self._config.get('simulate'))
            sleep(interval)

    def clear(self, simulate):
        total, used, free = shutil.disk_usage(self._current_path)

        logging.debug(
            f"Checking disk size for path ({self._current_path} against threshold ({self._config.threshold}): {free}"
        )

        if free < self._config.threshold:
            eligible_plot = self._get_plot()
            if eligible_plot:
                logging.info(f'Deleting eligible plot: {eligible_plot.name}')
                if not simulate:
                    eligible_plot.unlink(True)
            else:
                if len(self._paths) > 0:
                    self._current_path = Path(self._paths.pop(0))
                    logging.info(f'No eligible plots found, moving to next path: {self._current_path}')
                    self.clear(self._config.get('simulate'))
                else:
                    logging.info('Found no more paths with eligible plots')
        else:
            logging.debug(f"No action needed for {self._current_path}. Moving to next path")

    def _set_next_path(self):
        if len(self._paths) == 0:
            logging.info('No eligible paths found. Resetting')
            self._current_path = Path(self._paths.pop(0))
            logging.info(f'No eligible plots found, moving to next path: {self._current_path}')
            self.clear(self._config.get('simulate'))
        else:
            self._paths = self._config.raw.get('paths')


    def _get_plot(self) -> Optional[Path]:
        for plot in sorted(self._current_path.glob('*.plot')):
            if self._not_poolable(plot):
                return plot

        return None

    def _not_poolable(self, plot:Path) -> bool:
        res = re.match(r'(\d{4}-\d{2}-\d{2}-\d{2}-\d{2})', str(plot))
        if res:
            date = res.group(1)
            dt = datetime.strptime(date, '%y_%m_%d_%H_%M')

            logging.debug(
                f"Checking plot date ({dt.strftime('%y/%m/%d %H:%M')}) against threshold "
                f"({self._date.strftime('%y/%m/%d %H:%M')})"
            )
            if dt < self._date:
                return True

        return False

