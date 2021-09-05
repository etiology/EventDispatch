import datetime as dt
import uuid
from typing import Dict, Optional
from uuid import UUID

import pydantic
from pydantic import Field


def _current_utc_time():
    """ a timezone aware utc datetime """
    return dt.datetime.now(tz=dt.timezone.utc)


class Event(pydantic.BaseModel):
    """ An example of an event that is shared on an event stream

    This model contains metadata fields and a payload field called
    `EventData`.  The payload field in this example can contain any
    key/value data about what is being communicated by the producing
    application.

    General uses for the metadata fields:
     - `EventType`:         Used by downstream consumers who need to act on
                            specific event types
     - `EventID`:           Provides a way for tracking side effects caused by
                            this event.  Side effects should reference this
                            original `EventID` in some way.
     - `EventTimestampUTC`: An isoformatted datetime of when the event occurred
     - `EventData`:         Payload information that provides downstream
                            consumers information needed to act upon the event.

    """
    EventType: str
    EventID: UUID = Field(default_factory=uuid.uuid4)
    EventTimestampUTC: dt.datetime = Field(default_factory=_current_utc_time)
    EventData: Optional[Dict]

    class Config:
        json_encoders = {
            dt.date: lambda d: d.isoformat(),
            dt.datetime: lambda d: d.isoformat(),
        }

    def __str__(self):
        return f"{self.__class__.__name__}(EventType='{self.EventType}')"
