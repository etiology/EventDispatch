"""
# Event Registry

Register methods and functions to be called when a specific event is received

"""
from collections import defaultdict
from functools import wraps


class EventProcessorRegistry:
    """
    A collection of callables for events of specific types.  Methods
    and functions can be added to the registry via the `register_processor`
    decorator.  When an event is processed by the registry, all of the
    processors assigned to that event type will be passed the event to process.

    Examples:
        ```python

        # How to register a method for an event type

        registry = EventProcessorRegistry()

        # ...

        # Here we add the `my_event_processor` to the registry for
        # events of the type `OrderPlaced`
        @registry.register_processor("OrderPlaced")
        def reserve_product_inventory(event):
            # ...

        @registry.register_processor("ReadyToShip")
        def create_shipping_order(event):
            # ...

        @registry.register_processor("ItemShipped")
        def send_customer_shipment_receipt(event):
            # ...


        # Later events from the stream are passed to the registry
        # where it ensures all registered callables for that event
        # get a chance to run
        registry.async_process_event(event)
        ```
    """

    def __init__(self):
        self.event_processors = defaultdict(list)

    def register_processor(self, event_type: str) -> callable:
        """ A Decorator that registers a function to a specific event type

        The event stream consists of message that contain an 'EventType' identifier.  This
        decorator is used to ensure the function is passed these events when they occur in
        the stream.

        Args:
            event_type: case-insensitive event_type that the decorated function will receive

        Returns:
            callable
        """
        def decorated(fn):
            self.event_processors[event_type].append(fn)

            @wraps(fn)
            def wrapper(*args, **kwargs):
                return fn(*args, **kwargs)
            return wrapper
        return decorated

    def process_event(self, event) -> None:
        raise NotImplemented
