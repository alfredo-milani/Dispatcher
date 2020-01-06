from typing import List


class Rule(object):
    """

    """

    def __init__(self, name: str, formats: List[str], sources: List[str], destinations: List[str]):
        super().__init__()

        self.__name = name
        self.__formats = formats
        self.__sources = sources
        self.__destinations = destinations

    @property
    def name(self) -> str:
        return self.__name

    @property
    def formats(self) -> List[str]:
        return self.__formats

    @property
    def sources(self) -> List[str]:
        return self.__sources

    @property
    def destinations(self) -> List[str]:
        return self.__destinations
