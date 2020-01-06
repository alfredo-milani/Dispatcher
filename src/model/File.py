from os.path import splitext
from pathlib import Path
from shutil import copyfile

from model import Rule
from util import Validation


class File(object):
    """

    """

    def __init__(self, filename: str):
        super().__init__()

        self.__filename = filename
        self.__basename = Path(self.__filename).stem
        self.__ext = splitext(filename)[1]
        self.__file = f"{self.__basename}{self.__ext}"

    @property
    def filename(self) -> str:
        return self.__filename

    @property
    def ext(self) -> str:
        return self.__ext

    @property
    def basename(self) -> str:
        return self.__basename

    @property
    def file(self):
        return self.__file

    def exists(self) -> bool:
        try:
            Validation.path_exists(self.__filename)
            return True
        except FileNotFoundError:
            return False

    def delete(self) -> None:
        if not self.exists():
            raise FileNotFoundError

        Path(self.__filename).unlink()

    def copy_to(self, destinations: list) -> None:
        if not self.exists():
            raise FileNotFoundError(f"File '{self.__filename}' not exists and can not be copied")

        for destination in destinations:
            copyfile(self.__filename, f"{destination}/{self.__file}", follow_symlinks=False)

    def match_rule(self, rule: Rule) -> bool:
        follow_rule = False

        # checks if file extension match formats
        for f in rule.formats:
            if self.__ext.lower() == f.lower():
                follow_rule = True
                break
        if not follow_rule:
            return False

        # checks if creation/modification file which had triggered event handler
        #  belongs to at least one source in rule object
        # Note: this works only if file is created in the root directory of source
        #   (recursively search might take too long)
        for source in rule.sources:
            try:
                Validation.path_exists(f"{source}/{self.__file}")
                return True
            except FileNotFoundError:
                pass

        return False
