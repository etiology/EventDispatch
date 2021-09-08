import asyncio
import functools
import signal

from loguru import logger

from event_stream_processor.common.models import Event
from event_stream_processor.domain.entities.handler_registry import HandlerRegistry
from event_stream_processor.domain.interfaces.event_source import IEventSource
from event_stream_processor.exceptions import EmptyRegistryError


class Dispatcher:
    """ Processes events from a source by passing them to registered event handlers """

    def __init__(self, registry: HandlerRegistry, event_source: IEventSource):
        EmptyRegistryError.require_condition(
            message="Handler Registry is empty",
            expr=not registry.is_empty,
        )
        self.registry = registry
        self.event_source = event_source
        self._shutdown_flag_is_set = False

    def __str__(self):
        return f"{self.__class__.__name__}"

    def _set_loop_stop_signals(self, loop):
        """ creates an async loop with connected signal for shutdown """
        logger.debug(f"adding stop signals to loop")
        stop_signals = {"SIGINT", "SIGTERM"}
        for signame in stop_signals:
            loop.add_signal_handler(
                getattr(signal, signame),
                functools.partial(self._stop_async_loop, signame, loop),
            )

    def _stop_async_loop(self, signame, loop):
        logger.warning(f"Received {signame} signal - {self} is shutting down")
        self._shutdown_flag_is_set = True

    async def _send_to_dispatchers(self, event: Event, sleep_interval=0):
        """ asynchronously process the event via the registry """
        loop = asyncio.get_event_loop()
        self._set_loop_stop_signals(loop=loop)

        dispatch = asyncio.gather(
            functools.partial(self.registry.async_process_event, event=event)()
        )
        loop.run_until_complete(dispatch)
        await asyncio.sleep(sleep_interval)

    async def _start_processing_events(self):
        """ Start consuming events and dispatching them """
        with self.event_source as source:
            while True:
                event = source.get_event()
                if not event:
                    continue

                await self._send_to_dispatchers(event=event)
                if self._shutdown_flag_is_set:
                    print("Shutting down")
                    break
        logger.info(f"{self.__class__.__name__}.run() - exited due to stop call")

    def run(self) -> None:
        """ Read events from the source and dispatch them to the handlers """
        try:
            logger.info("[STARTING] Event Runner")
            asyncio.run(self._start_processing_events())
        except KeyboardInterrupt:
            logger.info("[STOPPED] Event Runner")
