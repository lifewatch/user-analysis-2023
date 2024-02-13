""" Scheduling the regular running functions of the main workflow (ingest / process / store)
"""

import logging
import time
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from .dereference import Dereference


log = logging.getLogger(__name__)


# https://apscheduler.readthedocs.io/en/3.x/userguide.html
class DereferenceScheduler(BlockingScheduler):
    def __init__(self, run_on_start: bool = True):
        time_delta = os.getenv("SCHEDULER_PERIOD", "300")
        timeprops: dict = dict(seconds=int(time_delta))

        # get the waittime before starting the scheduler
        waittime = os.getenv("SCHEDULER_WAIT", "10")
        time.sleep(int(waittime))

        super().__init__()
        self._run_on_start = run_on_start
        self.add_job(lambda: self.main_schedule(), "interval", **timeprops)

    def start(self):
        try:
            log.info("starting dereferencer scheduler")
            self.dereferencer = Dereference()
            if self._run_on_start:
                self.main_schedule()
            super().start()
        except (KeyboardInterrupt, SystemExit):
            log.info("execution interrupted")
        except Exception as e:
            log.exception(e)

    def main_schedule(self):
        log.info("starting main service flow")
        self.dereferencer.run_dereference()
