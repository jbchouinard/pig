from .human import Human  # noqa
from .linear import *
from .optimal import Optimal
from .roller import *
from .scorer import *


BOT_TYPES = {
    cls.__name__: cls
    for cls in [
        Optimal,
        Roller5,
        # Roller7,
        Scorer20,
        Scorer25,
        Linear5,
        # Linear10,
        # Linear20,
    ]
}
