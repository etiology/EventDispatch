class TestPytestFixtures:

    def test__kafka_config(self, kafka_config):
        assert kafka_config
        assert kafka_config.bootstrap_servers == "169.254.20.21:9092"
        assert kafka_config.topic_pattern == "unit_tests"
