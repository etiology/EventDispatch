import abc
from typing import Iterator, Any, Optional

from event_stream_processor.common.models import Event


class IEventSource:
    """ Interface class to accessing event data """

    def __iter__(self) -> Iterator[Event]:
        return self

    def __next__(self) -> Event:
        return self.get_event()

    def __enter__(self):
        self.connect_to_source()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    @property
    def cls_name(self) -> str:
        return self.__class__.__name__

    @abc.abstractmethod
    def connect_to_source(self) -> None:
        """ prepare to read events from a source """
        ...

    @abc.abstractmethod
    def get_event(self) -> Optional[Event]:
        """ fetch an event from the source """
        ...

    @abc.abstractmethod
    def close_connection(self) -> None:
        """ clean up any connections to the event source """
        ...
