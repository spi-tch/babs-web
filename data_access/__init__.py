from typing import Generic, TypeVar

from sqlalchemy.orm import Query

from .user import *

T = TypeVar('T')


class DBQuery(Generic[T], Query):
  pass
