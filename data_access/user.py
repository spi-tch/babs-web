import logging

from sqlalchemy import update
from sqlalchemy.exc import OperationalError

from exceptns import UserNotFoundException
from util.app import db

logger = logging.getLogger(__name__)


class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  uuid = db.Column(db.String, nullable=False, unique=True, index=True)
  first_name = db.Column(db.String(30), nullable=False)
  last_name = db.Column(db.String(30), nullable=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())
  email = db.Column(db.String(50), nullable=False, index=True)
  dob = db.Column(db.DATE, nullable=True)
  country = db.Column(db.String(2), nullable=True)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  timezone = db.Column(db.String(30), nullable=True)
  sub_expires_at = db.Column(db.TIMESTAMP, nullable=True)
  tier = db.Column(db.String, nullable=True)

  def __repr__(self):
    return f'User: {self.first_name} {self.last_name}; Country: {self.country}'


class StripeCustomer(db.Model):
  __tablename__ = 'stripe_customer'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  stripe_id = db.Column(db.String, nullable=False, unique=True, index=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())


class Quotes(db.Model):
  __tablename__ = 'quotes'
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  conf = db.Column(db.String, nullable=False)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                         onupdate=db.func.current_timestamp())


class WaitList(db.Model):
  __tablename__ = 'wait_list'
  id = db.Column(db.Integer, primary_key=True)
  created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
  email = db.Column(db.String, nullable=False, index=True)


def find_user_by_uuid(user_uuid: str) -> User:
  try:
    user = User.query.filter_by(uuid=str(user_uuid)).first()
    if user is None:
      raise UserNotFoundException('Unable to find user.')
    return user
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    raise UserNotFoundException('Unable to find user.')
  finally:
    db.session.close()


def find_user_by_id(user_id: int) -> User:
  try:
    user = User.query.filter_by(id=user_id).first()
    if user is None:
      raise None
    return user
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    raise UserNotFoundException('Unable to find user.')
  finally:
    db.session.close()


def create_user(user: User):
  try:
    db.session.add(user)
    db.session.commit()
  except Exception as e:
    logger.error(e)
    db.session.rollback()
  finally:
    db.session.close()


def update_user(user: User, _update: dict):
  try:
    statement = (update(User)
                 .where(User.uuid == user.uuid)
                 .values(**_update)
                 .execution_options(synchronize_session=False))

    db.session.execute(statement=statement)
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()


def create_waitlister(email: str):
  try:
    if _ := WaitList.query.filter(WaitList.email == email).first():
      return True
    else:
      waiter = WaitList(
        email=email,
      )
      db.session.add(waiter)
      # Thread(target=send_email, args=[email]).start()
    db.session.commit()
    return True
  except OperationalError:
    db.session.rollback()
    return False
  finally:
    db.session.close()


def get_stripe_customer(stripe_id: str) -> StripeCustomer:
  try:
    customer = StripeCustomer.query.filter_by(stripe_id=stripe_id).first()
    return customer
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    raise UserNotFoundException(f"User not found for stripe customer - {stripe_id}")
  finally:
    db.session.close()


def delete_stripe_customer(stripe_id: str):
  try:
    customer = StripeCustomer.query.filter_by(stripe_id=stripe_id).first()
    db.session.delete(customer)
    db.session.commit()
  except Exception as e:
    logger.error(e)
    db.session.rollback()
  finally:
    db.session.close()


def get_stripe_customer_by_user_id(user_id: int) -> StripeCustomer:
  try:
    customer = StripeCustomer.query.filter_by(user_id=user_id).first()
    return customer
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    raise UserNotFoundException(f"User not found for stripe customer - {user_id}")
  finally:
    db.session.close()


def create_stripe_customer(user_id, customer_id):
  customer: StripeCustomer = StripeCustomer(
    user_id=user_id,
    stripe_id=customer_id
  )
  try:
    db.session.add(customer)
    db.session.commit()
  except Exception as e:
    logger.error(e)
    db.session.rollback()
  finally:
    db.session.close()


def get_all_users():
  try:
    users = User.query.all()
    return users
  except Exception as e:
    print(e)
    db.session.rollback()
    return False
  finally:
      db.session.close()


def add_quote(user_id, conf):
  quote = Quotes(
    user_id=user_id,
    conf=conf,
  )
  try:
    db.session.add(quote)
    db.session.commit()
  except Exception as e:
    logger.error(e)
    db.session.rollback()
  finally:
    db.session.close()


def get_quote(user_id):
  try:
    quote = Quotes.query.filter_by(user_id=user_id).first()
    return quote
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()


def update_quote(user_id, conf):
  try:
    quote = Quotes.query.filter_by(user_id=user_id).first()
    quote.conf = conf
    db.session.commit()
    return True
  except Exception as e:
    logger.error(e)
    db.session.rollback()
    return False
  finally:
    db.session.close()
