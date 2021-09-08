# Kafka Event Source

The `KafkaEventSource` class inherits from `IEventSource` and provides 
the dispatcher access to events published to a kafka topic.  The source
requires a configuration containing connection values to the brokers,
their topic, and consumer group, and offset behavior.

`KafkaConfig` is a pyndatic [BaseSettings](https://pydantic-docs.helpmanual.io/usage/settings/)
instance which can pull values from environment variables or be explicitly
set during instantiation. 


----

::: event_stream_processor.infrastructure.kafka_event_source
    rendering:
        heading_level: 1 
        show_object_full_path: False
        show_category_heading: True
        show_source: True
