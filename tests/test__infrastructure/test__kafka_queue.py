from unittest.mock import MagicMock

import pytest

from event_stream_processor.infrastructure import kafka_event_source
from event_stream_processor.infrastructure.kafka_event_source import KafkaEventSource
from tests.support_factories.event_factory import EventFactory


class TestKafkaEventSource:

    @pytest.fixture(autouse=True)
    def setup(self, kafka_config, monkeypatch):
        self.cfg = kafka_config
        self.mock_consumer = None

    def patch_consumer_with_stub(self, monkeypatch, mock_consumer=None):
        """ defaults to a magic mock, but can be passed the kafka_consumer fixture instead """
        self.mock_consumer = mock_consumer or MagicMock()
        monkeypatch.setattr(
            target=kafka_event_source,
            name='Consumer',
            value=self.mock_consumer
        )

    def test__kafka_event_source__instantiate_class(self, monkeypatch):
        # GIVEN we have a configuration and a mocked consumer
        self.patch_consumer_with_stub(monkeypatch=monkeypatch)
        assert self.cfg

        # WHEN we instantiate a KafkaEventSource
        kafka_source = KafkaEventSource(config=self.cfg)

        # THEN we should get an instance of the class with a configured consumer
        assert kafka_source
        consumer_was_configured_once = self.mock_consumer.call_count == 1
        consumer_was_configured_correctly = self.mock_consumer.call_args.args[0] == {
            "bootstrap.servers": self.cfg.bootstrap_servers,
            "group.id": self.cfg.group_id,
            "auto.offset.reset": self.cfg.auto_offset_reset,
        }
        consumer_did_not_connect_to_server = not self.mock_consumer.subscribe.called

        assert consumer_was_configured_once
        assert consumer_was_configured_correctly
        assert consumer_did_not_connect_to_server

    def test__kafka_event_source__read_messages_from_topic(self, monkeypatch, kafka_consumer):
        # GIVEN a KafkaEventSource with a patched Consumer and messages in the topic
        self.patch_consumer_with_stub(monkeypatch, kafka_consumer())
        event_sample_1 = EventFactory(EventType="SimpleRead")
        event_sample_2 = EventFactory(EventType="SimpleRead")
        event_sample_3 = EventFactory(EventType="SimpleRead")
        self.mock_consumer.add_msg(event_sample_1.json())
        self.mock_consumer.add_msg(event_sample_2.json())
        self.mock_consumer.add_msg(event_sample_3.json())

        # WHEN we read 3 messages from the queue
        with KafkaEventSource(config=self.cfg) as kafka_source:
            read_messages = list()
            read_messages.append(kafka_source.get_event())
            read_messages.append(kafka_source.get_event())
            read_messages.append(kafka_source.get_event())

        # THEN we should have read our messages back
        assert read_messages
        assert read_messages[0] == event_sample_1
        assert read_messages[1] == event_sample_2
        assert read_messages[2] == event_sample_3
