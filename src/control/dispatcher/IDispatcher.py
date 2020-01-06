from abc import abstractmethod

from model import File


class IDispatcher(object):
    """
    Dispatcher interface
    """

    @abstractmethod
    def dispatch(self, file: File) -> None:
        """
        Method for dispatching file
        :param file: object which encapsulates information for file
        """
        raise NotImplementedError

    @abstractmethod
    def on_error(self, file: File = None,
                 exception: Exception = None) -> None:
        """
        Called on error
        :param file: object which encapsulates information for file
        :param exception: exception thrown
        """
        raise NotImplementedError

    @abstractmethod
    def on_success(self, file: File = None) -> None:
        """
        Called on strategy success
        :param file: object which encapsulates information for file
        """
        raise NotImplementedError
