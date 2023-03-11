import json

from configs.config import BabsConf
from constants import CONF_TYPE_CHANNEL, DEFAULT_CONFIG


class ChannelConf(BabsConf):
  def __init__(
      self,
      notification=False,
      quiet=False,
      on_pause=False,
      quiet_schedule=None,
      **params
  ):
    super(ChannelConf, self).__init__(
      conf_type=CONF_TYPE_CHANNEL,
      notification=notification,
      quiet=quiet,
      quiet_schedule=quiet_schedule,
      on_pause=on_pause,
    )

  @classmethod
  def from_string(cls, string):
    if not string:
      string = DEFAULT_CONFIG
    if string == DEFAULT_CONFIG:
      return cls(notification=True, quiet=False, on_pause=False, quiet_schedule={
        "days": [],
        "time": {
          "start": "00:00",
          "end": "00:00"
        }}
      )
    return cls(**json.loads(string))
