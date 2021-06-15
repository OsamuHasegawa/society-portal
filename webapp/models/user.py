from flask_login import UserMixin
from datetime import datetime, timedelta, timezone
from webapp.database import db

JST = timezone(timedelta(hours=+9), 'JST')


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=True)
    email = db.Column(db.TEXT, nullable=False)
    password = db.Column(db.TEXT, nullable=False)
    member_id = db.Column(db.TEXT, nullable=True)
    member_type_id = db.Column(db.Integer, db.ForeignKey('member_type.id'), nullable=True)
    member_validate = db.Column(db.Boolean, nullable=False, default=False)
    salt = db.Column(db.TEXT, nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    state = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
    token = db.Column(db.TEXT, nullable=True)
    token_period = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(JST), onupdate=datetime.now(JST))

    user_profile = db.relation('UserProfile', uselist=False, backref='user', cascade='all, delete-orphan')
    member_type = db.relation('MemberType', backref='user_profile')

    def __init__(self, name, email, password, member_id, member_type_id, member_validate, salt, role, state, token, token_period):
        self.name = name
        self.email = email
        self.password = password
        self.member_id = member_id
        self.member_type_id = member_type_id
        self.member_validate = member_validate
        self.salt = salt
        self.role = role
        self.state = state
        self.token = token
        self.token_period = token_period


class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    first_name = db.Column(db.TEXT, nullable=False)
    last_name = db.Column(db.TEXT, nullable=False)
    first_name_kana = db.Column(db.TEXT, nullable=False)
    last_name_kana = db.Column(db.TEXT, nullable=False)
    first_name_roman = db.Column(db.TEXT, nullable=False)
    last_name_roman = db.Column(db.TEXT, nullable=False)
    organization = db.Column(db.TEXT, nullable=False)
    department = db.Column(db.TEXT, nullable=True)
    address_type_id = db.Column(db.Integer, db.ForeignKey('address_type.id'), nullable=False)
    zip = db.Column(db.Integer, nullable=False)
    prefecture = db.Column(db.TEXT, nullable=False)
    municipalities = db.Column(db.TEXT, nullable=False)
    address1 = db.Column(db.TEXT, nullable=False)
    address2 = db.Column(db.TEXT, nullable=True)
    phone = db.Column(db.TEXT, nullable=False)

    address_type = db.relation('AddressType', backref='user_profile')

    def __init__(self, user_id, first_name, last_name, first_name_kana, last_name_kana, first_name_roman,
                 last_name_roman, organization, department, address_type_id, zip, prefecture, municipalities, address1, address2, phone):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.first_name_kana = first_name_kana
        self.last_name_kana = last_name_kana
        self.first_name_roman = first_name_roman
        self.last_name_roman = last_name_roman
        self.organization = organization
        self.department = department
        self.address_type_id = address_type_id
        self.zip = zip
        self.prefecture = prefecture
        self.municipalities = municipalities
        self.address1 = address1
        self.address2 = address2
        self.phone = phone

    def get_name(self):
        return self.last_name + ' ' + self.first_name


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, db.Sequence('role_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)

    # OrderNo = 0
    # ADMINISTRATOR = auto()
    # COMMITTEE = auto()
    # MEMBER = auto()
    # NO_ROLE = auto()


class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, db.Sequence('state_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)

    # ENABLE = auto()
    # DISABLE = auto()
    # SIGNUP = auto()
    # CHANGE_PASSWORD = auto()


class MemberType(db.Model):
    __tablename__ = 'member_type'

    id = db.Column(db.Integer, db.Sequence('member_type_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)
    label = db.Column(db.TEXT, nullable=False)

    # NON_MEMBER = "非会員"
    # MEMBER = "正会員"
    # MEMBER_TEACHER = "正会員（初等中等教育機関の教職員）"
    # MEMBER_STUDENT = "学生会員"
    # MEMBER_SUPPORT = "協賛会員"


class AddressType(db.Model):
    __tablename__ = 'address_type'

    id = db.Column(db.Integer, db.Sequence('address_type_id_seq'), primary_key=True)
    name = db.Column(db.TEXT, nullable=False)
    label = db.Column(db.TEXT, nullable=False)

    # HOME = "自宅"
    # BUSINESS = "正会員"


class LoginUser(UserMixin, User):

    def __init__(self, user, active=True, authenticated=False):
        self.name = user.name
        self.id = user.id
        self.active = active
        self.authenticated = authenticated

    def get_id(self):
        return self.id

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return self.authenticated
