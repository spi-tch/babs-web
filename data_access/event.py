import logging

from sqlalchemy.exc import OperationalError

from util.app import db

logger = logging.getLogger(__name__)


class BabsEvent(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False, index=True)
    type = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp(), index=True)
    channel = db.Column(db.String, nullable=True)
    data = db.Column(db.String)


def delete_user_events(user_id):
    try:
        delete_events_fn = BabsEvent.__table__.delete().where(BabsEvent.user_id.__eq__(user_id))
        # todo: Do not delete events, just edit sender_id to None
        db.session.execute(delete_events_fn)
        db.session.commit()
    except OperationalError as e:
        db.session.rollback()
        logger.error('Could not delete events.', e)
    finally:
        db.session.close()
