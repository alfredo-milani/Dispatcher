import logging
from typing import List

from control.dispatcher import BaseDispatcher
from model import File, Rule
from util import LogManager


class FileDispatcher(BaseDispatcher):
    """

    """

    __LOG = logging.getLogger(LogManager.Logger.DISPATCHER.value)

    def __init__(self, rules: List[Rule]):
        super().__init__()

        self.__rules = rules

    def prepare(self, file: File) -> None:
        super().prepare(file)
        super()._wait_file(file)

    def dispatch(self, file: File) -> None:
        FileDispatcher.__LOG.info(f"[DISPATCHING] '{file.filename}'")

        copied = False  # indicates that input file has been copied at least in one destination
        for rule in self.__rules:
            if file.match_rule(rule):
                FileDispatcher.__LOG.debug(f"[COPYING] '{file.filename}' to '{rule.destinations}")
                file.copy_to(rule.destinations)
                copied |= len(rule.destinations) > 0

        if copied:  # if file matches a rule, remove it
            FileDispatcher.__LOG.debug(f"[REMOVING] '{file.filename}'")
            file.delete()
        else:
            FileDispatcher.__LOG.debug(f"[SKIPPING] '{file.filename}': not match any rule")

    def on_success(self, file: File = None) -> None:
        super().on_success(file)
        FileDispatcher.__LOG.debug(f"[DISPATCH SUCCESS] '{file.filename}'")

    def on_error(self, file: File = None,
                 exception: Exception = None) -> None:
        super().on_error(file, exception)
        FileDispatcher.__LOG.warning(f"[DISPATCH ERROR] '{file.filename}'")
        FileDispatcher.__LOG.debug("[DISPATCH ERROR]", exc_info=True)

    @property
    def rules(self) -> List[Rule]:
        return self.__rules
