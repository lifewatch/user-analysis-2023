""" LWUA Dereferencer service entry-point
-- support service-like commands start/stop/status/reload
-- will start the cron-service-dispatch and the web UI endpoint
"""

from .daemon import Daemon
from .helpers import enable_logging, resolve_path
from dotenv import load_dotenv
from dereferencer import DereferenceScheduler
import sys
import logging

log = logging.getLogger(__name__)


class IngestDaemon(Daemon):
    def run(self):
        try:
            # setup
            log.info("setting up")
            scheduler: DereferenceScheduler = DereferenceScheduler()

            # action
            log.info("starting schedule")
            scheduler.start()

        except Exception as e:
            log.exception(e)
        finally:
            # teardown
            log.info("teardown")


def main():
    load_dotenv()
    enable_logging()

    pidfilename: str = "dereferencer-daemon.pid"
    # double dirname ends at parent!
    pidfile: str = resolve_path(pidfilename)

    IngestDaemon(pidfile)._cmd(sys.argv)


if __name__ == "__main__":
    main()
