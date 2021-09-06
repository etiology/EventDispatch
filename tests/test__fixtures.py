import pytest


class TestPytestFixtures:

    def test__kafka_config(self, kafka_config):
        assert kafka_config
        assert kafka_config.bootstrap_servers == "169.254.20.21:9092"
        assert kafka_config.topic_pattern == "unit_tests"

    def test__kafka_consumer(self, kafka_consumer):
        consumer = kafka_consumer()
        assert consumer
        assert not len(consumer.mock_queue)       # no messages in topic
        consumer.add_msg("spare parts")           # fake add message to topic
        assert len(consumer.mock_queue) == 1      # the topic has 1 message

        with pytest.raises(RuntimeError):         # close connections raise
            consumer.poll(0)
        consumer.subscribe(['fake_topic'])
        msg = consumer.poll(8.394)                # consume the message from the topic
        assert msg.value() == b"spare parts"      # verify it's our fake message
        assert consumer.poll(0) is None           # queue is now empty
