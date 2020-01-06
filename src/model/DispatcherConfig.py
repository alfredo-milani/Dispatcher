import ast
import configparser
import pathlib
import threading
from datetime import date

from util.Common import Common


class DispatcherConfig(dict):
    """

    """

    __INSTANCE = None
    __LOCK = threading.Lock()

    # Intern
    K_APP_NAME = "app_name"
    V_DEFAULT_APP_NAME = "Dispatcher"
    K_LOG_FILE = "log"
    V_DEFAULT_LOG_FILE = "/var/log/{}_{}.log"

    # Section
    S_GENERAL = "GENERAL"
    # Keys
    K_LOG_CONFIG_FILE = "log.config_file"
    V_DEFAULT_LOG_CONFIG_FILE = "{}/res/conf/log.ini"
    K_TMP = "tmp"
    V_DEFAULT_TMP = "/tmp"
    K_THREADS = "threads"
    V_DEFAULT_THREADS = 2

    # Section
    S_DISPATCHER = "DISPATCHER"
    # Keys
    K_FORMATS = "formats"
    V_DEFAULT_FORMATS = None
    K_SOURCES = "sources"
    V_DEFAULT_SOURCES = None
    K_SOURCES_TIMEOUT = "sources.timeout"
    V_DEFAULT_SOURCES_TIMEOUT = 1
    K_DESTINATIONS = "destinations"
    V_DEFAULT_DESTINATIONS = None
    K_RULES = "rules"
    V_DEFAULT_RULES = None

    def __init__(self):
        if DispatcherConfig.__INSTANCE is not None:
            raise DispatcherConfig.MultipleInstancesException(DispatcherConfig)

        super().__init__()

        DispatcherConfig.__INSTANCE = self
        self.__config_parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self.__upload_config()

    @classmethod
    def get_instance(cls) -> "DispatcherConfig":
        if cls.__INSTANCE is None:
            with cls.__LOCK:
                if cls.__INSTANCE is None:
                    DispatcherConfig()
        return cls.__INSTANCE

    def load_from(self, config_file: str) -> None:
        """

        :param config_file:
        :raise: SyntaxError if there is a syntax error in configuration file
        """
        path = pathlib.Path(config_file)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File '{config_file}' not exists")

        self.__config_parser.read(config_file)
        self.__upload_config()

    def __upload_config(self) -> None:
        """

        :raise: SyntaxError if there is a syntax error in configuration file
        """
        # intern
        self.__put_str(DispatcherConfig.K_APP_NAME, '', '', DispatcherConfig.V_DEFAULT_APP_NAME)
        self.__put_str(DispatcherConfig.K_LOG_FILE, '', '', DispatcherConfig.V_DEFAULT_LOG_FILE.format(self.app_name, date.today().strftime('%Y%m%d')))

        # section [GENERAL]
        self.__put_str(DispatcherConfig.K_LOG_CONFIG_FILE, DispatcherConfig.S_GENERAL, DispatcherConfig.K_LOG_CONFIG_FILE, DispatcherConfig.V_DEFAULT_LOG_CONFIG_FILE.format(Common.get_proj_root_path()))
        self.__put_str(DispatcherConfig.K_TMP, DispatcherConfig.S_GENERAL, DispatcherConfig.K_TMP, DispatcherConfig.V_DEFAULT_TMP)
        self.__put_int(DispatcherConfig.K_THREADS, DispatcherConfig.S_GENERAL, DispatcherConfig.K_THREADS, DispatcherConfig.V_DEFAULT_THREADS)

        # section [DISPATCHER]
        self.__put_dict(DispatcherConfig.K_FORMATS, DispatcherConfig.S_DISPATCHER, DispatcherConfig.K_FORMATS, DispatcherConfig.V_DEFAULT_FORMATS)
        self.__put_dict(DispatcherConfig.K_SOURCES, DispatcherConfig.S_DISPATCHER, DispatcherConfig.K_SOURCES, DispatcherConfig.V_DEFAULT_SOURCES)
        self.__put_float(DispatcherConfig.K_SOURCES_TIMEOUT, DispatcherConfig.S_DISPATCHER, DispatcherConfig.K_SOURCES_TIMEOUT, DispatcherConfig.V_DEFAULT_SOURCES_TIMEOUT)
        self.__put_dict(DispatcherConfig.K_DESTINATIONS, DispatcherConfig.S_DISPATCHER, DispatcherConfig.K_DESTINATIONS, DispatcherConfig.V_DEFAULT_DESTINATIONS)
        self.__put_dict(DispatcherConfig.K_RULES, DispatcherConfig.S_DISPATCHER, DispatcherConfig.K_RULES, DispatcherConfig.V_DEFAULT_RULES)

    def __put_obj(self, key: str, section: str, section_key: str, default: object = None) -> None:
        try:
            self[key] = self.__config_parser.get(section, section_key)
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    def __put_str(self, key: str, section: str, section_key: str, default: str = None) -> None:
        try:
            self[key] = str(self.__config_parser.get(section, section_key))
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    def __put_int(self, key: str, section: str, section_key: str, default: int = None) -> None:
        try:
            self[key] = int(self.__config_parser.get(section, section_key))
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    def __put_float(self, key: str, section: str, section_key: str, default: float = None) -> None:
        try:
            self[key] = float(self.__config_parser.get(section, section_key))
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    def __put_dict(self, key: str, section: str, section_key: str, default: dict = None) -> None:
        """

        :param key:
        :param section:
        :param section_key:
        :param default:
        :raise: SyntaxError if ast.literal_eval(node_or_string) fails parsing
            input string (syntax error in key/value pairs)
        """
        try:
            self[key] = ast.literal_eval(self.__config_parser.get(section, section_key))
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    def __put_bool(self, key: str, section: str, section_key: str, default: bool = None) -> None:
        try:
            self[key] = bool(self.__config_parser.get(section, section_key))
        except (configparser.NoOptionError, configparser.NoSectionError):
            self[key] = default

    @property
    def app_name(self) -> str:
        return self.get(DispatcherConfig.K_APP_NAME)

    @property
    def log_file(self) -> str:
        return self.get(DispatcherConfig.K_LOG_FILE)

    @property
    def general_log_config_file(self) -> str:
        return self.get(DispatcherConfig.K_LOG_CONFIG_FILE)

    @property
    def general_tmp(self) -> str:
        return self.get(DispatcherConfig.K_TMP)

    @property
    def general_threads(self) -> int:
        return self.get(DispatcherConfig.K_THREADS)

    @property
    def dispatcher_formats(self) -> dict:
        return self.get(DispatcherConfig.K_FORMATS)

    @property
    def dispatcher_sources(self) -> dict:
        return self.get(DispatcherConfig.K_SOURCES)

    @property
    def dispatcher_sources_timeout(self) -> float:
        return self.get(DispatcherConfig.K_SOURCES_TIMEOUT)

    @property
    def dispatcher_destinations(self) -> dict:
        return self.get(DispatcherConfig.K_DESTINATIONS)

    @property
    def dispatcher_rules(self) -> dict:
        return self.get(DispatcherConfig.K_RULES)

    def __str__(self):
        # chr(9) = '\t'
        # chr(10) = '\n'
        return f"### Configuration for {self.__class__.__name__}: " \
               f"{str().join(f'{chr(10)}{chr(9)}{{ {k} : {v} }}' for k, v in self.items())}"

    # Called if: Config + "string"
    def __add__(self, other):
        return str(self) + other

    # Called if: "string" + Config
    def __radd__(self, other):
        return other + str(self)

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
