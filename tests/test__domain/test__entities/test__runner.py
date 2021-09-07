import pytest

from event_stream_processor.domain.entities.dispatcher import EventDispatcher
from event_stream_processor.domain.entities.runner import EventRunner


class TestEventRunner:

    @pytest.fixture(autouse=True)
    def setup(self, mock_kafka_source):
        self.event_source = mock_kafka_source
        self.dispatcher = EventDispatcher()

    def test__event_runner__create_instance(self):
        # GIVEN we have a loaded dispatcher and event source
        self.dispatcher.register_async_processor("SampleEventType", lambda e: print(e))
        assert self.event_source

        # WHEN we instantiate the EventRunner class
        runner = EventRunner(dispatcher=self.dispatcher, event_source=self.event_source)

        # THEN we should receive an new runner instance with our dependencies present
        assert runner
        assert runner.event_source
        assert runner.dispatcher


