from functools import wraps
from typing import Optional, List, Union, Dict, Any
from unittest.mock import MagicMock

import pytest
from confluent_kafka import Message

from event_stream_processor.infrastructure.kafka_event_source import KafkaConfig


@pytest.fixture(scope="session")
def kafka_config() -> KafkaConfig:
    """ a test config for the KafkaEventSource interface """
    return KafkaConfig(
        bootstrap_servers="169.254.20.21:9092",
        group_id="pytest",
        auto_offset_reset="earliest",
        topic_pattern="unit_tests",
    )


@pytest.fixture(scope="function")
def kafka_consumer(kafka_config):
    class MockMessage:
        def __init__(self, value: bytes = None, error_message: str = None):
            self._value = value
            self._error = error_message

        def value(self, payload: Any = None):
            return self._value

        def error(self):
            return self._error

    class MockConsumer:
        def __init__(self, config: Dict = None):
            self.init_config = config if config else dict()
            self.mock_queue: List[bytes] = list()
            self.position = -1
            self.is_closed = True
            self.topic: List[str] = list()
            self.init_call_count = 0

        def __call__(self, *args, **kwargs):
            self.init_call_count += 1
            return self

        def subscribe(self, topics: List[str]):
            """ the consumer connects to brokers when we subscribe """
            self.topic = topics
            self.is_closed = False

        def poll(self, timeout: Union[int, float] = 0) -> Optional[MockMessage]:
            """ sort of mimics the kafka consumer's poll method """
            if self.is_closed:
                raise RuntimeError("Connection is closed")

            try:
                msg = self.mock_queue[self.position + 1]
                self.position += 1
                return MockMessage(value=msg)

            except IndexError:
                return None

        def close(self):
            self.is_closed = True

        def add_msg(self, msg: Union[str, bytes]) -> None:
            """ testing method where we can preload some fake data """
            msg_bytes = msg if isinstance(msg, bytes) else msg.encode('utf8')
            self.mock_queue.append(msg_bytes)
    return MockConsumer
