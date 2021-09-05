import pytest

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


