# Event Router

The **EventRouter** class provides a mechanism for assigning functions
to specific event types.  Registered functions will be passed their
subscribed events as they occur.  The router requires that all functions
registered to events be asynchronous.

::: event_stream_processor.domain.entities.event_router.EventRouter
    rendering:
        heading_level: 1 
        show_object_full_path: False
        show_category_heading: True
        show_source: True