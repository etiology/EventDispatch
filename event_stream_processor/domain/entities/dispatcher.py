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
    BadProcessorRegistrationError,
)


class EventDispatcher:
    """
    Methods and functions can be added to the EventDispatcher via the `register_async_processor`
    decorator.  When an event is processed by the router, all of the processors
    assigned to that event type will be passed the event to process.

    Examples:
        Assign events to functions using a decorator:
        ```python

        dispatcher = EventDispatcher()

        # register `reserve_product_inventory` to the `OrderPlaced` event type
        @dispatcher.register_async_processor("OrderPlaced")
        async def reserve_product_inventory(event):
            # ...

        # register `create_shipping_order` to the `ReadyToShip` event type
        @dispatcher.register_async_processor("ReadyToShip")
        async def create_shipping_order(event):
            # ...

        # register `send_customer_shipment_receipt` to the `ItemShipped` event type
        @dispatcher.register_async_processor("ItemShipped")
        def send_customer_shipment_receipt(event):
            # ...
        ```

        Assign events to a method of a class:
        ```python

        class MyMerchExample:
            def __init__(self):
                # ... perhaps this class needs to be
                # initialized before handling events
                ...

            async def reserve_product_inventory(self, event):
                ...

            async def create_shipping_order(self, event):
                ...

            async def send_customer_shipment_receipt(self, event):
                ...

        merch = MyMerchExample(...)
        dispatcher = EventDispatcher()
        dispatcher.register_async_processor("OrderPlaced", merch.reserve_product_inventory)
        dispatcher.register_async_processor("ReadyToShip", merch.create_shipping_order)
        dispatcher.register_async_processor("ItemShipped", merch.send_customer_shipment_receipt)

        ```

        Dispatching events to the registered handlers can be done by calling
        the `async_process_event()` method and passing in the event to process:
        ```python

        # ... pass events into the dispatcher
        for event in event_stream.read():
            await dispatcher.async_process_event(event)
        ```
    """

    def __init__(self):
        self.event_processors = defaultdict(list)

    @property
    def is_empty(self) -> bool:
        return not bool(self.event_processors)

    def register_async_processor(
        self, event_type: str, method: callable = None
    ) -> callable:
        """A Decorator that registers an async function for specific even type

        The event stream consists of message that contain an 'EventType' identifier.  This
        decorator is used to ensure the function is passed these events when they occur in
        the stream.

        Notes:
            An event processor function needs to accept an Event model as an argument

        Args:
            event_type: case-insensitive event_type that the decorated function will receive
            method: (Optional) Used if the callable being registered is a method on a class

        Returns:
            callable
        """

        if method:
            self.event_processors[event_type].append(method)
            return
        else:
            # when decorating a function
            def decorated(fn):
                @wraps(fn)
                def wrapper(*args, **kwargs):
                    return fn(*args, **kwargs)

                with BadProcessorRegistrationError.check_expressions(
                    "event processor"
                ) as check:
                    check(inspect.iscoroutinefunction(fn), "needs to be a coroutine"),
                    check(
                        "event" in inspect.signature(fn).parameters,
                        "needs to accept an 'event' as a parameter",
                    )
                self.event_processors[event_type].append(fn)
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
