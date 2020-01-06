class Common(object):
    """

    """

    @staticmethod
    def is_installed(binary: str) -> bool:
        """
        Check whether 'name' is on PATH and marked as executable
        :param binary: binary to check
        :return: True iff binary is in PATH, False otherwise
        """
        from shutil import which
        return which(binary) is not None

    @staticmethod
    def get_proj_root_path() -> str:
        from pathlib import Path
        return Path(__file__).parent.parent.parent
