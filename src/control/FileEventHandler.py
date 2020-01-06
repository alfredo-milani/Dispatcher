import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

from watchdog.events import FileSystemEvent, FileSystemMovedEvent, FileSystemEventHandler

from control.dispatcher import FileDispatcher
from model import File, Rule
from util import LogManager
from util.Validation import Validation, ValidationException


class FileEventHandler(FileSystemEventHandler):
    """
    This class handles the events of creations and move to of a file.

    This class rely on FileDispatcher to perform copy/remove of files.
    """

    __LOG = logging.getLogger(LogManager.Logger.OBSERVER.value)

    DEFAULT_MAX_THREADS = 2

    def __init__(self, rules: List[Rule], max_threads: int = DEFAULT_MAX_THREADS):
        super().__init__()

        self.__dispatcher = FileDispatcher(rules)
        self.__executor = ThreadPoolExecutor(max_workers=max_threads)

    def __submit(self, filename) -> None:
        try:
            Validation.is_file(filename)
            Validation.has_extension(filename)
        except ValidationException.MissingExtensionError:
            FileEventHandler.__LOG.debug(f"[SKIPPING] file '{filename}': no extension")
            return
        except FileNotFoundError:
            FileEventHandler.__LOG.debug(f"[SKIPPING] file '{filename}': no regular file")
            return

        self.__executor.submit(
            self.__dispatcher.execute,
            File(filename)
        )

    def on_created(self, event: FileSystemEvent) -> None:
        super().on_created(event)
        FileEventHandler.__LOG.debug(f"[CREATED] file '{event.src_path}'")
        self.__submit(event.src_path)

    def on_moved(self, event: FileSystemMovedEvent) -> None:
        super().on_moved(event)
        FileEventHandler.__LOG.debug(f"[MOVED] file '{event.src_path}' to '{event.dest_path}'")
        self.__submit(event.dest_path)

    def shutdown(self) -> None:
        # shutdown threads
        self.__executor.shutdown(wait=True)
