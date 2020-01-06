import logging
import logging.config
import sys
import threading
from enum import Enum


class LogManager(object):
    """

    """

    __INSTANCE = None
    __LOCK = threading.Lock()

    _L_ROOT = None
    _L_OBSERVER = None
    _L_DISPATCHER = None

    _H_CONSOLE = None
    _LOG_FILE = None
    _H_FILE = None

    _F_GENERAL = None

    def __init__(self):
        if LogManager.__INSTANCE is not None:
            raise LogManager.MultipleInstancesException(LogManager)

        super().__init__()

        LogManager.__INSTANCE = self

    @classmethod
    def get_instance(cls) -> "Logger":
        if cls.__INSTANCE is None:
            with cls.__LOCK:
                if cls.__INSTANCE is None:
                    LogManager()
        return cls.__INSTANCE

    @classmethod
    def load(cls) -> None:
        from model import DispatcherConfig
        # formatters
        cls._F_GENERAL = LogManager.__configure_f_general()
        # handlers
        cls._H_CONSOLE = LogManager.__configure_h_console()
        cls._H_FILE = LogManager.__configure_h_file(DispatcherConfig.get_instance().log_file)
        # loggers
        cls._L_ROOT = LogManager.__configure_l_root()
        cls._L_OBSERVER = LogManager.__configure_l_observer()
        cls._L_DISPATCHER = LogManager.__configure_l_dispatcher()

    @classmethod
    def load_from(cls, log_config_file: str) -> None:
        from util import Validation
        Validation.path_exists(log_config_file, f"File '{log_config_file}' not exists")
        Validation.is_file(log_config_file, f"'{log_config_file}' is not a regular file")

        logging.config.fileConfig(fname=log_config_file)
        # loggers
        cls._L_ROOT = logging.getLogger(LogManager.Logger.ROOT.value)
        cls._L_OBSERVER = logging.getLogger(LogManager.Logger.OBSERVER.value)
        cls._L_DISPATCHER = logging.getLogger(LogManager.Logger.DISPATCHER.value)

    class Logger(Enum):
        ROOT = "root"
        OBSERVER = "observer"
        DISPATCHER = "dispatcher"

    @classmethod
    def get(cls, logger: Logger) -> logging.Logger:
        if logger is None:
            raise ValueError

        if logger == cls.Logger.ROOT:
            return cls._L_ROOT
        elif logger == cls.Logger.OBSERVER:
            return cls._L_OBSERVER
        elif logger == cls.Logger.DISPATCHER:
            return cls._L_DISPATCHER
        else:
            raise NotImplementedError

    @staticmethod
    def __configure_l_root() -> logging.Logger:
        root_logger = logging.getLogger(LogManager.Logger.ROOT.value)
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(LogManager._H_CONSOLE)
        return root_logger

    @staticmethod
    def __configure_l_observer() -> logging.Logger:
        observer_logger = logging.getLogger(LogManager.Logger.OBSERVER.value)
        observer_logger.setLevel(logging.DEBUG)
        observer_logger.propagate = 0
        observer_logger.addHandler(LogManager._H_CONSOLE)
        observer_logger.addHandler(LogManager._H_FILE)
        return observer_logger

    @staticmethod
    def __configure_l_dispatcher() -> logging.Logger:
        dispatcher_logger = logging.getLogger(LogManager.Logger.DISPATCHER.value)
        dispatcher_logger.setLevel(logging.DEBUG)
        dispatcher_logger.propagate = 0
        dispatcher_logger.addHandler(LogManager._H_CONSOLE)
        dispatcher_logger.addHandler(LogManager._H_FILE)
        return dispatcher_logger

    @staticmethod
    def __configure_h_console() -> logging.Handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(LogManager._F_GENERAL)
        return console_handler

    @staticmethod
    def __configure_h_file(log_filename: str) -> logging.Handler:
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LogManager._F_GENERAL)
        return file_handler

    @staticmethod
    def __configure_f_general() -> logging.Formatter:
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
