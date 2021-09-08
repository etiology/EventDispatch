![Python](https://img.shields.io/badge/Python-3.9-green?style=flat)


# Event Dispatcher

The [Event Source Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
provides a way for applications to communicate to other systems through a series
of events.  Each event contains state change data.  Downstream services can listen 
for these events and take action when they are received.

The `Dispatch` class provides a mechanism for subscribing our custom functions
to these events.  The dispatcher reads events from a source and then 
propagates them to registered callback functions.  


## Usage Example

```python

from event_stream_processor import HandlerRegistry
from event_stream_processor import Dispatcher
from event_stream_processor import KafkaEventSource
from event_stream_processor import KafkaConfig
from event_stream_processor.common.models import Event


# setup event handler registry
handler_registry = HandlerRegistry()


# register our event handler function
@handler_registry.register_async_processor("OrderRequest")
async def process_customer_orders(event: Event):
    pass

 
if __name__ == '__main__':
    # start the dispatcher
    kafka_config = KafkaConfig(
        bootstrap_servers="127.0.0.1:9092",
        group_id="example_group",
        auto_offset_reset="earliest",
        topic_pattern="event_dispatcher_demo",
    )
    runner = Dispatcher(
        event_source=KafkaEventSource(config=kafka_config), 
        registry=handler_registry
    )
    runner.run()


```



----

## Development Notes
Requirements
 - [poetry](https://python-poetry.org/)

This project uses [poetry](https://python-poetry.org/) for dependency management.  To 
install project dependencies run the following command in the project directory:
```shell
poetry install
```
see [poetry's basic usage](https://python-poetry.org/docs/basic-usage/#installing-dependencies-only)
for more information


### Generate Documentation
You can build a local copy of the docs by running the following command:
```shell
mkdocs build
```

### Git Hooks
You can add the project's git hooks to your local configuration by running the 
following command:
```shell
git config --local core.hooksPath .githooks/
```


