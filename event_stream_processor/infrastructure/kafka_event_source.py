from typing import Optional

import pydantic
from confluent_kafka import Consumer
from loguru import logger

from event_stream_processor.common.models import Event
from event_stream_processor.domain.interfaces.event_source import IEventSource


class KafkaConfig(pydantic.BaseSettings):
    """ Configuration class to setup a KafkaEventSource """

    bootstrap_servers: str
    group_id: str
    auto_offset_reset: str
    topic_pattern: str


class KafkaEventSource(IEventSource):
    """ Read events from a kafka topic """

    def __init__(self, config: KafkaConfig):
        super().__init__()
        self.configuration = config
        self._consumer = Consumer(
            {
                "bootstrap.servers": self.configuration.bootstrap_servers,
                "group.id": self.configuration.group_id,
                "auto.offset.reset": self.configuration.auto_offset_reset,
            }
        )

    def connect_to_source(self) -> None:
        self._consumer.subscribe([self.configuration.topic_pattern])

    def get_event(self) -> Optional[Event]:
        """ read next message """
        try:
            msg = self._consumer.poll(1.0)
            if msg is None:
                return None
            if msg.error():
                logger.warning("KafkaEventSource error: {}".format(msg.error()))
                return None

            return Event.parse_raw(msg.value())
        except pydantic.error_wrappers.ValidationError as err:
            logger.error(f"{self.cls_name}.get_event() deserialization error - {err}")

    def close_connection(self) -> None:
        self._consumer.close()
