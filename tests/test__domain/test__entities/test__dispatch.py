import pytest

from event_stream_processor.domain.entities.dispatch import Dispatcher
from event_stream_processor.domain.entities.handler_registry import HandlerRegistry


class TestDispatcher:

    @pytest.fixture(autouse=True)
    def setup(self, mock_kafka_source):
        self.event_source = mock_kafka_source
        self.dispatcher = HandlerRegistry()

    def test__event_runner__create_instance(self):
        # GIVEN we have a loaded dispatcher and event source
        self.dispatcher.register_async_processor("SampleEventType", lambda e: print(e))
        assert self.event_source

        # WHEN we instantiate the Dispatcher class
        runner = Dispatcher(dispatcher=self.dispatcher, event_source=self.event_source)

        # THEN we should receive an new runner instance with our dependencies present
        assert runner
        assert runner.event_source
        assert runner.dispatcher


