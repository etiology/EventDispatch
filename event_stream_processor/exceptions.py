from buzz import Buzz


class EventProcessorUncaughtException(Buzz):
    """ An error that is not handled by the running event processor function """

    pass


class BadProcessorRegistration(Buzz):
    """ The callable being registered is not accepted """

    pass
