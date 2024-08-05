import logging

from util.app import db

logger = logging.getLogger(__name__)


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(),
                           onupdate=db.func.current_timestamp())
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False)
    success = db.Column(db.Boolean, nullable=False)
    stripe_id = db.Column(db.String, nullable=False, unique=True, index=True)


def create_payment(user_uuid, amount, currency, success, stripe_id):
    try:
        payment = Payment(user_uuid=user_uuid, amount=amount, currency=currency, success=success, stripe_id=stripe_id)
        db.session.add(payment)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return False
    finally:
        db.session.close()


def get_payment_for_user(user_uuid):
    try:
        payments = Payment.query.filter_by(user_uuid=user_uuid).first()
        return payments
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return None
    finally:
        db.session.close()


def update_payment(payment_id, success):
    try:
        payment = Payment.query.filter_by(id=payment_id).first()
        payment.success = success
        db.session.commit()
        return True
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return False
    finally:
        db.session.close()
