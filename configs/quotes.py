import json

from configs.config import BabsConf
from constants import DEFAULT_CONFIG


class QuoteConf(BabsConf):
    def __init__(
        self,
        daily_message=False,
        hour=0,
        minute=0,
        category=None,
        **params
    ):
        super(QuoteConf, self).__init__(
            daily_message=daily_message,
            hour=hour,
            minute=minute,
            category=category
        )

    @classmethod
    def from_string(cls, string=None):
        if not string or string == DEFAULT_CONFIG:
            return cls(daily_message=False, hour=0, minute=0, category=None)
        _dict = json.loads(string)
        return cls(**_dict)
