import logging
import logging.config
import sys
import threading
from enum import Enum

from util import Validation


class LogManager(object):
    """

    """

    __INSTANCE = None
    __LOCK = threading.Lock()

    _LOGGER_ROOT = None
    _LOGGER_OBSERVER = None
    _LOGGER_DISPATCHER = None

    _HANDLER_CONSOLE = None
    _LOG_FILENAME = None
    _HANDLER_FILE = None

    _FORMATTER = None

    def __init__(self):
        if LogManager.__INSTANCE is not None:
            raise LogManager.MultipleInstancesException(LogManager)

        super().__init__()

        LogManager.__INSTANCE = self

    @classmethod
    def get_instance(cls) -> "LogManager":
        if cls.__INSTANCE is None:
            with cls.__LOCK:
                if cls.__INSTANCE is None:
                    LogManager()
        return cls.__INSTANCE

    @classmethod
    def load(cls, log_filename: str = None) -> None:
        if log_filename is not None:
            from pathlib import Path
            from util import Validation
            parent_directory = Path(log_filename).parent
            Validation.is_dir_writeable(parent_directory, f"Directory '{parent_directory}' must exists and be writable")

        with cls.__LOCK:
            # formatters
            cls._FORMATTER = LogManager.__configure_formatter()
            # handlers
            cls._HANDLER_CONSOLE = LogManager.__configure_handler_console()
            if log_filename is not None:
                LogManager._LOG_FILENAME = log_filename
                cls._HANDLER_FILE = LogManager.__configure_handler_file(log_filename)
            # loggers
            cls._LOGGER_ROOT = LogManager.__configure_logger_root()
            cls._LOGGER_OBSERVER = LogManager.__configure_logger_observer()
            cls._LOGGER_DISPATCHER = LogManager.__configure_logger_dispatcher()

    @classmethod
    def load_from(cls, log_config_file: str) -> None:
        from util import Validation
        Validation.is_file_readable(log_config_file, f"File '{log_config_file}' *must* exists and be readable")

        with cls.__LOCK:
            logging.config.fileConfig(fname=log_config_file)
            # loggers
            cls._LOGGER_ROOT = logging.getLogger(LogManager.Logger.ROOT.value)
            cls._LOGGER_OBSERVER = logging.getLogger(LogManager.Logger.OBSERVER.value)
            cls._LOGGER_DISPATCHER = logging.getLogger(LogManager.Logger.DISPATCHER.value)

    class Logger(Enum):
        ROOT = "root"
        OBSERVER = "observer"
        DISPATCHER = "dispatcher"

    @classmethod
    def get(cls, logger: Logger) -> logging.Logger:
        Validation.not_none(logger)

        if logger == cls.Logger.ROOT:
            return cls._LOGGER_ROOT
        elif logger == cls.Logger.OBSERVER:
            return cls._LOGGER_OBSERVER
        elif logger == cls.Logger.DISPATCHER:
            return cls._LOGGER_DISPATCHER
        else:
            raise NotImplementedError

    @classmethod
    def shutdown(cls) -> None:
        logging.shutdown()

    @staticmethod
    def __configure_logger_root() -> logging.Logger:
        root_logger = logging.getLogger(LogManager.Logger.ROOT.value)
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(LogManager._HANDLER_CONSOLE)
        return root_logger

    @staticmethod
    def __configure_logger_observer() -> logging.Logger:
        observer_logger = logging.getLogger(LogManager.Logger.OBSERVER.value)
        observer_logger.setLevel(logging.DEBUG)
        observer_logger.propagate = 0
        observer_logger.addHandler(LogManager._HANDLER_CONSOLE)
        if LogManager._LOG_FILENAME is not None:
            observer_logger.addHandler(LogManager._HANDLER_FILE)
        return observer_logger

    @staticmethod
    def __configure_logger_dispatcher() -> logging.Logger:
        dispatcher_logger = logging.getLogger(LogManager.Logger.DISPATCHER.value)
        dispatcher_logger.setLevel(logging.DEBUG)
        dispatcher_logger.propagate = 0
        dispatcher_logger.addHandler(LogManager._HANDLER_CONSOLE)
        if LogManager._LOG_FILENAME is not None:
            dispatcher_logger.addHandler(LogManager._HANDLER_FILE)
        return dispatcher_logger

    @staticmethod
    def __configure_handler_console() -> logging.Handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        # console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(LogManager._FORMATTER)
        return console_handler

    @staticmethod
    def __configure_handler_file(log_filename: str) -> logging.Handler:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LogManager._FORMATTER)
        return file_handler

    @staticmethod
    def __configure_formatter() -> logging.Formatter:
        f = "[%(levelname)-7s] | %(asctime)s | [%(name)s] %(funcName)s (%(module)s:%(lineno)s) - %(message)s"
        return logging.Formatter(f)

    class MultipleInstancesException(Exception):
        """

        """

        def __init__(self, *args):
            super().__init__(f"Singleton instance: a second instance of {args[0]} can not be created")

        def __str__(self):
            if len(self.args) == 0:
                return ""
            if len(self.args) == 1:
                return str(self.args[0])
            return str(self.args[0][0])
