from unittest.mock import MagicMock

import pytest

from event_stream_processor.infrastructure import kafka_event_source
from event_stream_processor.infrastructure.kafka_event_source import KafkaEventSource


class TestKafkaEventSource:

    @pytest.fixture(autouse=True)
    def setup(self, kafka_config, monkeypatch):
        self.cfg = kafka_config
        self.mock_consumer = MagicMock()
        monkeypatch.setattr(
            target=kafka_event_source,
            name='Consumer',
            value=self.mock_consumer
        )

    def test__kafka_event_source__instantiate_class(self):
        # GIVEN we have a configuration
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
