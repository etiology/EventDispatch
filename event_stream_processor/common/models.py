from typing import Dict, Optional

import pydantic


class Event(pydantic.BaseModel):
    """ An example of an event that is shared on an event stream """
    EventType: str
    EventData: Optional[Dict]
