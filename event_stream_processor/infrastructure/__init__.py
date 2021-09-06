"""

Infrastructure modules

These modules implement the `domain.interfaces` and provides connections to
external externals sources like databases, files, streams, etc.  Each
interface module should contain it's own configuration class

"""
import importlib

__all__ = [

]


# lazy load submodules - see PEP-562: https://www.python.org/dev/peps/pep-0562/
def __getattr__(name):
    if name in __all__:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
