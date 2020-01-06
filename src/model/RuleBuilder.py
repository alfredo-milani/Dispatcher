from typing import List

from model.Rule import Rule
from util import Validation


class RuleBuilder(object):
    """

    """

    K_FORMATS = "formats"
    K_SOURCES = "sources"
    K_DESTINATIONS = "destinations"

    def __init__(self):
        super().__init__()

    @classmethod
    def _retrieve_format_list(cls, rule: dict, formats: dict) -> List[str]:
        formats_list = []
        for frt in rule[cls.K_FORMATS]:
            for _frt in formats[frt]:
                formats_list.append(_frt.lower())
        return formats_list

    @classmethod
    def _retrieve_source_list(cls, rule: dict, sources: dict) -> List[str]:
        return [sources[src] for src in rule[cls.K_SOURCES]]

    @classmethod
    def _retrieve_destination_list(cls, rule: dict, destinations: dict) -> List[str]:
        return [destinations[dst] for dst in rule[cls.K_DESTINATIONS]]

    @classmethod
    def build_list(cls, rules: dict, formats: dict,
                   sources: dict, destinations: dict) -> List[Rule]:
        rules_list = []
        for rule in rules:
            rules_list.append(Rule(
                rule,
                cls._retrieve_format_list(rules[rule], formats),
                cls._retrieve_source_list(rules[rule], sources),
                cls._retrieve_destination_list(rules[rule], destinations)
            ))

        return rules_list
