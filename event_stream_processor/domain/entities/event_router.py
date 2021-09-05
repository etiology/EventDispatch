"""
# Event Registry

Register methods and functions to be called when a specific event is received

"""
import asyncio
import inspect
from collections import defaultdict
from functools import wraps

from loguru import logger

from event_stream_processor.common.models import Event
from event_stream_processor.exceptions import (
    BadProcessorRegistration,
)


class EventRouter:
    """
    Methods and functions can be added to the EventRouter via the `register_async_processor`
    decorator.  When an event is processed by the router, all of the processors
    assigned to that event type will be passed the event to process.

    Examples:
        ```python

        event_router = EventRouter()

        # register `reserve_product_inventory` to the `OrderPlaced` event type
        @event_router.register_async_processor("OrderPlaced")
        async def reserve_product_inventory(event):
            # ...

        # register `create_shipping_order` to the `ReadyToShip` event type
        @event_router.register_async_processor("ReadyToShip")
        async def create_shipping_order(event):
            # ...

        # register `send_customer_shipment_receipt` to the `ItemShipped` event type
        @event_router.register_async_processor("ItemShipped")
        def send_customer_shipment_receipt(event):
            # ...

        # ... pass events into the event_router
        for event in event_stream.read():
            await event_router.async_process_event(event)
        ```
    """

    def __init__(self):
        self.event_processors = defaultdict(list)

    def register_async_processor(self, event_type: str) -> callable:
        """A Decorator that registers an async function for specific even type

        The event stream consists of message that contain an 'EventType' identifier.  This
        decorator is used to ensure the function is passed these events when they occur in
        the stream.

        Notes:
            An event processor function needs to accept an Event model as an argument

        Args:
            event_type: case-insensitive event_type that the decorated function will receive

        Returns:
            callable
        """

        def decorated(fn):
            with BadProcessorRegistration.check_expressions("event processor") as check:
                check(inspect.iscoroutinefunction(fn), "needs to be a coroutine"),
                check(
                    "event" in inspect.signature(fn).parameters,
                    "needs to accept an 'event' as a parameter",
                )
            self.event_processors[event_type].append(fn)

            @wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)

            return wrapper

        return decorated

    async def async_process_event(self, event: Event, timeout: float = 2.0) -> None:
        """Run all processors registered to this type of event

        Args:
            event: The data to pass to the registered event processors
            timeout: Maximum time in seconds that an event processor is allowed to run

        """
        logger.info(f"Processing - {event}")
        event_processing_coroutines = [
            asyncio.wait_for(registered_processor(event), timeout=timeout)
            for registered_processor in self.event_processors[event.EventType]
        ]
        results = await asyncio.gather(
            *event_processing_coroutines, return_exceptions=True
        )

        # Log any failures from the event processors
        err_results = [result for result in results if isinstance(result, Exception)]
        if err_results:
            logger.error(
                f"async_process_event - uncaught error from an event processor: {err_results}"
            )
