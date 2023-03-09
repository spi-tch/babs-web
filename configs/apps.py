import json

from configs.config import BabsConf
from constants import DEFAULT_CONFIG, GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME, NOTION_APP_NAME


class AppConfig(BabsConf):
  def __init__(
      self,
      name,
      **params
  ):
    super(AppConfig, self).__init__(name=name, **params)

  @classmethod
  def from_string(cls, name, string):
    if not string:
      string = DEFAULT_CONFIG

    if string != DEFAULT_CONFIG:
      return cls(**json.loads(string))

    if name == GOOGLE_MAIL_APP_NAME:
      return cls(name=GOOGLE_MAIL_APP_NAME, notification=True, notification_filter=True, summarization=False)
    elif name == GOOGLE_CAL_APP_NAME:
      return cls(name=GOOGLE_CAL_APP_NAME, notification=True)
    elif name == NOTION_APP_NAME:
      return cls(name=NOTION_APP_NAME, summarization=True)
    else:
      raise ValueError(f'{name} app not supported.')
