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
    receipt_addressed = db.Column(db.TEXT, nullable=True)
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


class Presentation(db.Model):
    __tablename__ = 'presentation'

    id = db.Column(db.Integer, db.Sequence('presentation_id_seq'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    title = db.Column(db.TEXT, nullable=False)
    abstract = db.Column(db.TEXT, nullable=False)
    keyword = db.Column(db.TEXT, nullable=True)
    keyword_free = db.Column(db.TEXT, nullable=True)
    copyright = db.Column(db.TEXT, nullable=False)
    paper_status = db.Column(db.TEXT, nullable=True)
    is_cancel = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))

    def __init__(self, user_id, event_id, type, title, abstract, keyword, keyword_free, _copyright, paper_status, is_cancel):
        self.user_id = user_id
        self.event_id = event_id
        self.type = type
        self.title = title
        self.abstract = abstract
        self.keyword = keyword
        self.keyword_free = keyword_free
        self.copyright = _copyright
        self.paper_status = paper_status
        self.is_cancel = is_cancel


class CoAuthor(db.Model):
    __tablename__ = 'co_author'

    id = db.Column(db.Integer, db.Sequence('co_author_id_seq'), primary_key=True)
    member_id = db.Column(db.TEXT, nullable=True)
    email = db.Column(db.TEXT, nullable=True)
    first_name = db.Column(db.TEXT, nullable=False)
    last_name = db.Column(db.TEXT, nullable=False)
    first_name_kana = db.Column(db.TEXT, nullable=False)
    last_name_kana = db.Column(db.TEXT, nullable=False)
    first_name_roman = db.Column(db.TEXT, nullable=False)
    last_name_roman = db.Column(db.TEXT, nullable=False)
    organization = db.Column(db.TEXT, nullable=False)
    department = db.Column(db.TEXT, nullable=True)

    def __init__(self, member_id, email, first_name, last_name, first_name_kana, last_name_kana, first_name_roman, last_name_roman, organization, department):
        self.member_id = member_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.first_name_kana = first_name_kana
        self.last_name_kana = last_name_kana
        self.first_name_roman = first_name_roman
        self.last_name_roman = last_name_roman
        self.organization = organization
        self.department = department


class PresentationCoAuthor(db.Model):
    __tablename__ = 'presentation_co_author'

    id = db.Column(db.Integer, db.Sequence('presentation_co_author_id_seq'), primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    co_author_id = db.Column(db.Integer, db.ForeignKey('co_author.id'), nullable=False)

    def __init__(self, presentation_id, co_author_id):
        self.presentation_id = presentation_id
        self.co_author_id = co_author_id


# class Paper(db.Model):
#     __tablename__ = 'paper'
#
#     id = db.Column(db.Integer, db.Sequence('presentation_id_seq'), primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)


# class PresentationPaper(db.Model):
#     __tablename__ = 'presentation_paper'
#
#     id = db.Column(db.Integer, db.Sequence('presentation_id_seq'), primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

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
