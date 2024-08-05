from typing import Generic, TypeVar

from sqlalchemy.orm import Query

from .user import *
from .auth import *
from .channels import *
from .developer import *
from .apps import *
from .event import *
from .subscription import *

T = TypeVar('T')


class DBQuery(Generic[T], Query):
  pass
