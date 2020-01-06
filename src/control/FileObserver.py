import logging.config
from pathlib import Path
from typing import Dict

from watchdog.observers import Observer

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
    #  - programmatic logs
    #  - unit test

    __LOG = None

    _DISPATCHER_CONFIG = None

    PY_VERSION_MIN = (3, 7)

    def __init__(self, dispatcher_config: DispatcherConfig):
        """

        :param dispatcher_config:
        :raise
        """
        super().__init__()

        FileObserver._DISPATCHER_CONFIG = dispatcher_config
        self.__dir_obs_dict = None
        self.__event_handler = None

        # Validate python version
        self.__validate_py_version(FileObserver.PY_VERSION_MIN)
        # Load loggers
        self.__init_loggers(dispatcher_config.general_log_config_file)
        # Validate rules
        self.__validate_rules()
        # Check permissions
        self.__check_permissions()

        self.__dir_obs_dict = self._fill_dict(dispatcher_config.dispatcher_sources)
        self.__event_handler = FileEventHandler(RuleBuilder.build_list(
            dispatcher_config.dispatcher_rules,
            dispatcher_config.dispatcher_formats,
            dispatcher_config.dispatcher_sources,
            dispatcher_config.dispatcher_destinations
        ))

    @classmethod
    def __validate_py_version(cls, min_version):
        Validation.python_version(
            min_version,
            f"Python version required >= {min_version}"
        )

    @classmethod
    def __init_loggers(cls, log_config_file):
        Validation.is_file_readable(
            log_config_file,
            f"Log configuration file *must* exists and be readable '{log_config_file}'"
        )

        # Loading log's configuration file
        logging.config.fileConfig(fname=log_config_file)
        FileObserver.__LOG = logging.getLogger(LogManager.Logger.OBSERVER.value)

    def _fill_dict(self, directories: Dict[str, str]) -> Dict[str, Observer]:
        directories_list = [directories[src] for src in directories]
        observers_list = [Observer(timeout=self._DISPATCHER_CONFIG.dispatcher_sources_timeout) for _ in range(len(directories_list))]
        return dict(zip(directories_list, observers_list))

    def __validate_rules(self) -> None:
        """

        :raise TypeError
        :raise ValueError
        """
        formats = self._DISPATCHER_CONFIG.dispatcher_formats
        sources = self._DISPATCHER_CONFIG.dispatcher_sources
        destinations = self._DISPATCHER_CONFIG.dispatcher_destinations
        rules = self._DISPATCHER_CONFIG.dispatcher_rules

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
        sources = self._DISPATCHER_CONFIG.dispatcher_sources
        destinations = self._DISPATCHER_CONFIG.dispatcher_destinations

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
            FileObserver.__LOG.info(f"Start observing {directory}")

        for directory in self.__dir_obs_dict:
            self.__dir_obs_dict[directory].join()

    def start(self) -> None:
        FileObserver.__LOG.debug(chr(10) + FileObserver._DISPATCHER_CONFIG)
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
                FileObserver.__LOG.info(f"Stop observing {directory}")
        except RuntimeError as e:
            FileObserver.__LOG.debug(f"{e}", exc_info=True)

        FileObserver.__LOG.debug("Shutting down logging service")
        logging.shutdown()

    def stop(self) -> None:
        FileObserver.__LOG.info("*** STOP *** monitoring")

        FileObserver.__LOG.info("Cleanup")
        self.__cleanup()

        FileObserver.__LOG.info("Exit")
