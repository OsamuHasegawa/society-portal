from datetime import datetime, timedelta, timezone
from webapp.database import db
from webapp.models import User

JST = timezone(timedelta(hours=+9), 'JST')


class Society(db.Model):
    __tablename__ = 'society'

    id = db.Column(db.Integer, db.Sequence('society_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)
    english_name = db.Column(db.TEXT, nullable=True)
    abbreviation = db.Column(db.TEXT, nullable=True)
    url = db.Column(db.TEXT, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, db.Sequence('event_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)
    english_name = db.Column(db.TEXT, nullable=True)
    url = db.Column(db.TEXT, nullable=True)
    event_form_id = db.Column(db.Integer, db.ForeignKey('event_form.id'), nullable=True)
    has_papers = db.Column(db.Boolean, nullable=True)
    has_social_gathering = db.Column(db.Boolean, nullable=True)
    date = db.Column(db.ARRAY(db.DateTime), nullable=True)
    attend_period = db.Column(db.DateTime, nullable=True)
    presenting_papers_period = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))

    event_form = db.relationship('EventForm', backref='event')
    event_fee = db.relationship('EventFee', backref='event')
    # event_user = db.relationship('EventUser')


class EventForm(db.Model):
    __tablename__ = 'event_form'

    id = db.Column(db.Integer, db.Sequence('event_form_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)
    label = db.Column(db.TEXT, nullable=False)


class EventFee(db.Model):
    __tablename__ = 'event_fee'
    __table_args__ = (db.UniqueConstraint('event_id', 'member_type_id', name='event_fee_uix_event_id_member_type_id'), {})

    id = db.Column(db.Integer, db.Sequence('event_fee_id_seq'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    member_type_id = db.Column(db.Integer, db.ForeignKey('member_type.id'), nullable=False)
    participation = db.Column(db.Integer, nullable=False, default=0)
    papers = db.Column(db.Integer, nullable=False, default=0)
    social_gathering = db.Column(db.Integer, nullable=False, default=0)
    corporate_exhibition = db.Column(db.Integer, nullable=False, default=0)
    web_advertising_banner = db.Column(db.Integer, nullable=False, default=0)
    web_advertising_small = db.Column(db.Integer, nullable=False, default=0)
    web_advertising_medium = db.Column(db.Integer, nullable=False, default=0)
    web_advertising_large = db.Column(db.Integer, nullable=False, default=0)


class EventAttendUser(db.Model):
    __tablename__ = 'event_attend_user'
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='event_attend_uix_user_id_event_id'), {})

    id = db.Column(db.Integer, db.Sequence('event_attend_user_id_seq'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    attend_date = db.Column(db.ARRAY(db.DateTime), nullable=True)
    expect_papers = db.Column(db.Boolean, nullable=True, default=False)
    attend_social_gathering = db.Column(db.Boolean, nullable=True, default=False)
    payment_status = db.Column(db.TEXT, nullable=True)
    cancel = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))

    event = db.relationship('Event', backref='event_attend_user')

    def __init__(self, user_id, event_id, attend_date, expect_papers, attend_social_gathering, payment_status):
        self.user_id = user_id
        self.event_id = event_id
        self.attend_date = attend_date
        self.expect_papers = expect_papers
        self.attend_social_gathering = attend_social_gathering
        self.payment_status = payment_status

# class EventPresentationUser(db.Model):
#     __tablename__ = 'event_presentation_user'
#     __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='event_presentation_uix_user_id_event_id'), {})
#
#     id = db.Column(db.Integer, db.Sequence('event_presentation_user_id_seq'), primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
#     papers = db.Column(db.Boolean, nullable=True, default=False)
#     attend_social_gathering = db.Column(db.Boolean, nullable=True, default=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
#     updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))
#
#     event = db.relationship('Event', backref='event_attend_user')
