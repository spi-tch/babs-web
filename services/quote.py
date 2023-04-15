import logging
import logging
import os

import requests

from configs import QuoteConf
from constants import GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME, DEFAULT_CONFIG
from data_access import User, get_quote, add_quote, update_quote

logger = logging.getLogger(__name__)
GOOGLE_APPS = [GOOGLE_MAIL_APP_NAME, GOOGLE_CAL_APP_NAME]
SCHEDULER_HOST = os.getenv("SCHEDULER_BASE_URL")


class QuoteService:
  @classmethod
  def add_or_update_quote(cls, user: User, conf: dict) -> [bool, str]:
    __quote = get_quote(user.id)
    job_id = __quote.job_id if __quote else None

    if not job_id:  # Then we need to create a new job
      if conf["daily_message"]:
        response = requests.post(f"{SCHEDULER_HOST}/quote",
                                 json={"category": conf["category"],
                                       "hour": conf["hour"],
                                       "minute": conf["minute"],
                                       "timezone": user.timezone or "Africa/Lagos",
                                       "uuid": user.uuid
                                       })
        if response.status_code != 200:
          logger.error(response)
          return False, 'Error when trying to schedule quotes.'
        job_id = response.json().get("job_id", None)
      if not __quote:
        add_quote(user.id, f"{conf}", job_id=job_id)
      else:
        update_quote(user.id, f"{conf}", job_id=job_id)
      return True, 'Quote config added.'

    else:  # Then we need to update or delete the job
      if conf["daily_message"]:
        response = requests.patch(f"{SCHEDULER_HOST}/quote",
                                  json={"category": conf["category"],
                                        "hour": conf["hour"],
                                        "minute": conf["minute"],
                                        "timezone": user.timezone or "Africa/Lagos",
                                        "uuid": user.uuid
                                        })
        if response.status_code != 200:
          logger.error(response)
          return False, 'Error when trying to schedule quotes.'
        job_id = response.json().get("job_id", None)
      else:
        requests.delete(f"{SCHEDULER_HOST}/quote", json={"job_id": job_id})
        job_id = None
      update_quote(user.id, f"{conf}", job_id=job_id)
      return True, 'Quote config updated.'

  @classmethod
  def get_quote(cls, user: User) -> [bool, str, dict]:
    quote = get_quote(user.id)
    if not quote:  # Every user must have a quote record.
      add_quote(user.id, DEFAULT_CONFIG, None)
      quote = get_quote(user.id)
    quote_conf = QuoteConf.from_string(quote.conf)
    return True, 'Quote config found.', quote_conf
