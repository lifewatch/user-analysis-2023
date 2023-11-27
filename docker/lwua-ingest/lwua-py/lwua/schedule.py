""" Scheduling the regular running functions of the main workflow (ingest / process / store)
"""
import logging
import time
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from .ingest import run_ingest


log = logging.getLogger(__name__)


def main_schedule():
    log.info("starting main service flow")
    run_ingest()


# https://apscheduler.readthedocs.io/en/3.x/userguide.html
class LWUAScheduler(BlockingScheduler):
    def __init__(self, run_on_start: bool = True):
        time_delta = os.getenv("SCHEDULER_DELTA", "30")
        timeprops: dict = dict(seconds=int(time_delta))

        # get the waittime before starting the scheduler
        waittime = os.getenv("SCHEDULER_WAIT", "0")
        time.sleep(int(waittime))

        super().__init__()
        self._run_on_start = run_on_start
        self.add_job(lambda: main_schedule(), "interval", **timeprops)

    def start(self):
        try:
            if self._run_on_start:
                main_schedule()
            super().start()
        except (KeyboardInterrupt, SystemExit):
            log.info("execution interrupted")
