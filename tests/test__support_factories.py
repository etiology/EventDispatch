
import pytest

from tests.support_factories.event_factory import EventFactory


class TestSupportFactories:

    @pytest.mark.parametrize('model_factory', [
        EventFactory
    ])
    def test__create_model__from_factory(self, model_factory):
        model = model_factory()
        assert model
        assert model.json()
