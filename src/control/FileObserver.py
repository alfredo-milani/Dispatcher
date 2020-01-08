from pathlib import Path
from typing import Dict

from watchdog.observers import Observer

import __version__
from control.FileEventHandler import FileEventHandler
from model import DispatcherConfig, RuleBuilder
from util import Validation, LogManager


class FileObserver(object):
    """
    This class provide observable behavior for multiple directories
        and only one handler.

    One Observer for each source directory to observe.
    All Observers have the same FileEventHandler.
    """

    # TODO
    #  - add verbose and debug cli option
    #  - unit test

    __LOG = None

    PY_VERSION_MIN = (3, 7)

    def __init__(self, dispatcher_config: DispatcherConfig):
        """

        :param dispatcher_config:
        :raise
        """
        super().__init__()

        print(f"version: {__version__.__version__}")

        # Validate python version
        Validation.python_version(FileObserver.PY_VERSION_MIN, f"Python version required >= {FileObserver.PY_VERSION_MIN}")

        self.__dispatcher_config = dispatcher_config

        # Load loggers
        self.__init_loggers(dispatcher_config.log_filename)
        # Validate rules
        self.__validate_rules()
        # Check permissions
        self.__check_permissions()

        self.__dir_obs_dict = self.__fill_dict(dispatcher_config.dispatcher_sources)
        self.__event_handler = FileEventHandler(
            RuleBuilder.build_list(
                dispatcher_config.dispatcher_rules,
                dispatcher_config.dispatcher_formats,
                dispatcher_config.dispatcher_sources,
                dispatcher_config.dispatcher_destinations
            ),
            dispatcher_config.general_threads
        )

    @classmethod
    def __init_loggers(cls, log_filename: str) -> None:
        log_manager = LogManager.get_instance()
        log_manager.load(log_filename)
        FileObserver.__LOG = log_manager.get(LogManager.Logger.OBSERVER)
        FileObserver.__LOG.critical("DDD " + hex(id(log_manager)))

    def __fill_dict(self, directories: Dict[str, str]) -> Dict[str, Observer]:
        directories_list = [directories[src] for src in directories]
        timeout = self.__dispatcher_config.dispatcher_sources_timeout
        observers_list = [Observer(timeout=timeout) for _ in range(len(directories_list))]
        return dict(zip(directories_list, observers_list))

    def __validate_rules(self) -> None:
        """

        :raise TypeError
        :raise ValueError
        """
        formats = self.__dispatcher_config.dispatcher_formats
        sources = self.__dispatcher_config.dispatcher_sources
        destinations = self.__dispatcher_config.dispatcher_destinations
        rules = self.__dispatcher_config.dispatcher_rules

        Validation.is_dict(formats, "Formats not specified")
        Validation.is_true(
            len(formats) > 0,
            "Formats must be at least one"
        )
        Validation.is_dict(sources, "Source directories not specified")
        Validation.is_true(
            len(sources) > 0,
            "Directories to observe must be at least one"
        )
        Validation.is_dict(destinations, "Destination directories not specified")
        Validation.is_true(
            len(destinations) > 0,
            "Destination directories must be at least one"
        )
        Validation.is_dict(rules, "Rules not specified")
        Validation.is_true(
            len(rules) > 0,
            "Rules must be at least one"
        )

    def __check_permissions(self):
        """
        Check permissions on directories before performing the operations

        :raise ValueError if input directory is equal to output directory
        :raise NotADirectoryError
        :raise PermissionError
        :raise LinksError
        """
        sources = self.__dispatcher_config.dispatcher_sources
        destinations = self.__dispatcher_config.dispatcher_destinations

        for source in sources:
            Validation.is_dir(
                sources[source],
                f"Missing input directory '{sources[source]}'"
            )
            Validation.can_read(
                sources[source],
                f"Missing read permission on '{sources[source]}'"
            )
            Validation.can_write(
                sources[source],
                f"Missing write permission on '{sources[source]}'"
            )

        for destination in destinations:
            try:
                Validation.is_dir_writeable(
                    destinations[destination],
                    f"Directory '{destinations[destination]}' *must* exists and be writable"
                )
            except NotADirectoryError:
                parent_directory = Path(destinations[destination]).parent
                Validation.can_write(
                    parent_directory,
                    f"Missing write permission on '{parent_directory}'"
                )
                FileObserver.__LOG.info(f"Creating missing destination directory '{destinations[destination]}'")
                # create if not exists
                Path(destinations[destination]).mkdir(parents=True, exist_ok=True)

            for source in sources:
                Validation.are_symlinks(
                    sources[source],
                    destinations[destination],
                    f"Input ('{sources[source]}') and output ('{destinations[destination]}') directory can not be the same (or symlinks)"
                )

    def __observe(self) -> None:
        # Start observing directories
        for directory in self.__dir_obs_dict:
            self.__dir_obs_dict[directory].schedule(
                self.__event_handler,
                directory,
                recursive=False
            )
            self.__dir_obs_dict[directory].start()
            FileObserver.__LOG.debug(f"Start observing {directory}")

        for directory in self.__dir_obs_dict:
            self.__dir_obs_dict[directory].join()

    def start(self) -> None:
        FileObserver.__LOG.debug(chr(10) + self.__dispatcher_config)
        FileObserver.__LOG.info("*** START *** monitoring")

        try:
            self.__observe()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            FileObserver.__LOG.fatal(f"Error occurred: {e}")
            FileObserver.__LOG.debug(f"{e}", exc_info=True)

    def __cleanup(self) -> None:
        FileObserver.__LOG.debug("Detaching event handlers")
        self.__event_handler.shutdown()

        FileObserver.__LOG.debug("Shutting down observers")
        try:
            for directory in self.__dir_obs_dict:
                self.__dir_obs_dict[directory].unschedule_all()
                # stop observer if interrupted
                self.__dir_obs_dict[directory].stop()
                # Wait until the thread terminates before exit
                self.__dir_obs_dict[directory].join()
                FileObserver.__LOG.debug(f"Stop observing {directory}")
        except RuntimeError as e:
            FileObserver.__LOG.debug(f"{e}", exc_info=True)

        FileObserver.__LOG.debug("Shutting down logging service")
        LogManager.get_instance().shutdown()

    def stop(self) -> None:
        FileObserver.__LOG.info("*** STOP *** monitoring")

        FileObserver.__LOG.debug("Cleanup")
        self.__cleanup()

        FileObserver.__LOG.debug("Exit")
