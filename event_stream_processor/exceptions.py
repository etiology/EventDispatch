from buzz import Buzz


class BadProcessorRegistrationError(Buzz):
    """ The callable being registered is not accepted """

    pass


class EmptyDispatcherError(Buzz):
    """ The event dispatcher is empty and can not be used """

    pass
