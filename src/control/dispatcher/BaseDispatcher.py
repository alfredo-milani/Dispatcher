import time
from abc import ABC
from os.path import getsize

from control.dispatcher import IDispatcher
from model import File


class BaseDispatcher(ABC, IDispatcher):
    """

    """

    TRANSFER_DATA_POLL = 0.5

    def execute(self, file: File) -> None:
        """
        DO NOT EDIT OR OVERRIDE THIS METHOD
        :param file: object which encapsulates information for file
        """
        self.prepare(file)

        try:
            self.dispatch(file)
        except Exception as e:
            return self.on_error(file, e)

        return self.on_success(file)

    def prepare(self, file: File) -> None:
        pass

    def on_error(self, file: File = None,
                 exception: Exception = None) -> None:
        pass

    def on_success(self, file: File = None) -> None:
        pass

    @classmethod
    def _wait_file(cls, file: File,
                   poll_time: float = TRANSFER_DATA_POLL) -> None:
        """
        This function blocks until file is not completely transferred on disk
        This action is mandatory on low speed network, otherwise file could be
         read even if it is not completely transferred on the server
        :param file: object to obtain filename
        :param poll_time: poll time
        """
        size = -1
        while size != getsize(file.filename):
            size = getsize(file.filename)
            time.sleep(poll_time)
