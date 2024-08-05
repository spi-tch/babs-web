import logging

from util.app import db

logger = logging.getLogger(__name__)


class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String, nullable=False)
    plan = db.Column(db.String, nullable=False)
    payment_provider = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    next_subscription_at = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String, nullable=False)


def get_user_subscription(user_uuid) -> Subscription:
    try:
        subscription = Subscription.query.filter_by(user_uuid=user_uuid).first()
        return subscription
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return None
    finally:
        db.session.close()


def create_subscription(user_uuid, plan, status, provider, next_subscription_at):
    try:
        subscription = Subscription(
            user_uuid=user_uuid, plan=plan,
            status=status, payment_provider=provider,
            next_subscription_at=next_subscription_at
        )
        db.session.add(subscription)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return False
    finally:
        db.session.close()


def update_subscription(user_uuid, status, provider, next_subscription_at=None):
    try:
        subscription = Subscription.query.filter_by(user_uuid=user_uuid).first()
        subscription.status = status
        subscription.payment_provider = provider

        if next_subscription_at is not None:
            subscription.next_subscription_at = next_subscription_at

        db.session.commit()
        return True
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return False
    finally:
        db.session.close()
