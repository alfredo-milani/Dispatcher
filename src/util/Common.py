class Common(object):
    """

    """

    @staticmethod
    def get_proj_root_path() -> str:
        from pathlib import Path
        return Path(__file__).parent.parent.parent
