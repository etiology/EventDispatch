import pytest

from event_stream_processor.common.models import Event
from event_stream_processor.domain.entities.event_router import EventRouter
from event_stream_processor.exceptions import BadProcessorRegistration
from tests.support_factories.event_factory import EventFactory


class TestEventRouter:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.example_processor1_was_called = False
        self.example_processor2_was_called = False

    def _register_example_fn_processor1(self, reg: EventRouter, event_type: str, err=None):
        """ adds a test event processor to the registry """

        @reg.register_async_processor(event_type)
        async def example_event_processor1(event: Event):
            self.example_processor1_was_called = True
            if err:
                raise err

    def _register_example_fn_processor2(self, reg: EventRouter, event_type: str, err=None):
        """ adds a test event processor to the registry """

        @reg.register_async_processor(event_type)
        async def example_event_processor2(event: Event):
            self.example_processor2_was_called = True
            if err:
                raise err

    def test__event_processor_registry__create_empty(self):
        # WHEN we instantiate the EventRouter class
        registry = EventRouter()

        # THEN we should receive an instance of the registry class
        assert registry

    def test__event_processor_registry__register_async_processing_function(self):
        # GIVEN we have an empty event registry
        registry = EventRouter()
        registry_started_empty = len(registry.event_processors) == 0

        # WHEN we register a coroutine to a specific event type
        @registry.register_async_processor("SomeEventType")
        async def processing_method(event):
            pass

        # THEN the registry should include this method in it's event type mapping
        event_type_has_assigned_processors = registry.event_processors["SomeEventType"]

        assert registry_started_empty
        assert event_type_has_assigned_processors

    def test__event_processor_registry__register_async_processing_function__requires_event_as_parameter(self):
        # GIVEN we have an empty event registry
        registry = EventRouter()
        registry_started_empty = len(registry.event_processors) == 0

        with pytest.raises(BadProcessorRegistration, match=r".*needs to accept an 'event' as a parameter.*"):
            # WHEN we register a coroutine to that does not accept an event as a parameter
            # THEN it should raise a BadProcessorRegistration error
            @registry.register_async_processor("SomeEventType")
            async def processing_method(thing_a):
                pass

    def test__event_processor_registry__register_async_processing_function__raises_on_non_async_function(self):
        # GIVEN we have an empty event registry
        registry = EventRouter()
        registry_started_empty = len(registry.event_processors) == 0

        with pytest.raises(BadProcessorRegistration, match=r".*coroutine.*"):
            # WHEN we register a non async function to a specific event type
            # THEN a BadProcessorRegistration error should be raised
            @registry.register_async_processor("SomeEventType")
            def processing_method(event):
                pass

    @pytest.mark.asyncio
    async def test__event_processor_registry__async_process_event__considers_event_type(self, event_loop):
        # GIVEN a registry with event processors
        reg = EventRouter()
        self._register_example_fn_processor1(reg=reg, event_type='Foo')
        self._register_example_fn_processor2(reg=reg, event_type='Other')
        assert not any([self.example_processor1_was_called, self.example_processor2_was_called])
        the_event = EventFactory(EventType='Foo')

        # WHEN the registry processes the event
        await reg.async_process_event(the_event)

        # THEN the processor 1 should have been passed the event
        assert self.example_processor1_was_called
        assert not self.example_processor2_was_called

    @pytest.mark.asyncio
    async def test__event_processor_registry__async_process_event__multiple_processor_functions(self, event_loop):
        # GIVEN a registry with two registered event processors
        reg = EventRouter()
        self._register_example_fn_processor1(reg=reg, event_type='Foo')
        self._register_example_fn_processor2(reg=reg, event_type='Foo')
        assert not any([self.example_processor1_was_called, self.example_processor2_was_called])
        the_event = EventFactory(EventType='Foo')

        # WHEN the registry processes the event
        await reg.async_process_event(the_event)

        # THEN the processors should have been passed the event and ran
        assert self.example_processor1_was_called
        assert self.example_processor2_was_called

    @pytest.mark.asyncio
    async def test__event_processor_registry__async_process_event__multiple_processor_functions(self, event_loop):
        # GIVEN classes with registered methods as event processors
        reg = EventRouter()

        class Base:
            def __init__(self):
                self.method_called = False

            async def process_event(self, event: Event):
                self.method_called = True

        class Example1(Base): pass

        class Example2(Base): pass

        eg1 = Example1()
        eg2 = Example2()
        reg.register_async_processor('Foo', eg1.process_event)
        reg.register_async_processor('Foo', eg2.process_event)

        assert not any([eg1.method_called])
        the_event = EventFactory(EventType='Foo')

        # WHEN the registry processes the event
        await reg.async_process_event(the_event)

        # THEN the processors should have been passed the event and ran
        assert eg1.method_called

    @pytest.mark.asyncio
    async def test__event_processor_registry__async_process_event__no_interrupt_from_processor_error(self, event_loop):
        # GIVEN a registry with event processors
        reg = EventRouter()
        self._register_example_fn_processor1(reg=reg, event_type='Foo')
        self._register_example_fn_processor2(reg=reg, event_type='Foo', err=ValueError)
        assert not any([self.example_processor1_was_called, self.example_processor2_was_called])
        the_event = EventFactory(EventType='Foo')

        # WHEN the registry processes the event
        await reg.async_process_event(the_event)

        # THEN the processors should have been passed the event and ran
        assert self.example_processor1_was_called
        assert self.example_processor2_was_called
