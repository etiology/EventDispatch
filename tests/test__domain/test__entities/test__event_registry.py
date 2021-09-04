import pytest

from event_stream_processor.domain.entities.event_registry import EventProcessorRegistry
from event_stream_processor.exceptions import BadProcessorRegistration


class TestExampleClass:

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    def test__event_processor_registry__create_empty(self):
        # WHEN we instantiate the EventProcessorRegistry class
        registry = EventProcessorRegistry()

        # THEN we should receive an instance of the registry class
        assert registry

    def test__event_registry__register_async_processing_function(self):
        # GIVEN we have an empty event registry
        registry = EventProcessorRegistry()
        registry_started_empty = len(registry.event_processors) == 0

        # WHEN we register a coroutine to a specific event type
        @registry.register_async_processor("SomeEventType")
        async def processing_method(event):
            pass

        # THEN the registry should include this method in it's event type mapping
        event_type_has_assigned_processors = registry.event_processors["SomeEventType"]

        assert registry_started_empty
        assert event_type_has_assigned_processors

    def test__event_registry__register_async_processing_function__raises_on_non_async_function(self):
        # GIVEN we have an empty event registry
        registry = EventProcessorRegistry()
        registry_started_empty = len(registry.event_processors) == 0

        with pytest.raises(BadProcessorRegistration, match=r".*coroutine.*"):
            # WHEN we register a non async function to a specific event type
            # THEN a BadProcessorRegistration error should be raised
            @registry.register_async_processor("SomeEventType")
            def processing_method(event):
                pass



