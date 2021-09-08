from buzz import Buzz


class BadProcessorRegistrationError(Buzz):
    """ The callable being registered is not accepted """

    pass


class EmptyRegistryError(Buzz):
    """ The event registry is empty and can not be used """

    pass
