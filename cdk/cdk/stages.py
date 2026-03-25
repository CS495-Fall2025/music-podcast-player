import os
from enum import Enum, auto


class Stage(Enum):
    DEVELOPMENT = auto()
    PRODUCTION = auto()


CURRENT_STAGE = (
    Stage.PRODUCTION if os.getenv("DEPLOY_ENVIRONMENT", "Production") == "Production"
    else Stage.DEVELOPMENT
)
