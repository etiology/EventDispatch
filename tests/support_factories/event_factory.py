import datetime as dt

import factory
from factory import fuzzy

from event_stream_processor.common.models import Event


class EventFactory(factory.Factory):
    """ A factory-boy Event model factory """

    EventType = factory.fuzzy.FuzzyText()
    EventID = factory.Faker('uuid4')
    EventTimestampUTC = factory.Faker('date_time_this_year', tzinfo=dt.timezone.utc)

    class Meta:
        model = Event
