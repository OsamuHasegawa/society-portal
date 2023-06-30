import hashlib
import mimetypes
import urllib

import jaconv
import os
import random
import string
import pdfkit

from distutils.util import strtobool

from flask import Blueprint, jsonify, send_file
from flask import current_app
from flask import flash
from flask import make_response
from flask import render_template
from flask import request, redirect, url_for
from flask import session
from flask_mail import Message
from flask_login import login_required, login_user, logout_user, current_user

from webapp.definition.role import Role as RoleDefinition
from webapp.definition.state import State as StateDefinition
from webapp.definition.payment_status import PaymentStatus as PaymentStatusDefinition
from webapp.mail import mail
from webapp.models.society import *
from webapp.models.user import *
from webapp.login_manager import login_manager

urls = Blueprint('urls', __name__)

@login_manager.user_loader
def load_user(user_id):
    return LoginUser.query.filter(LoginUser.id == user_id).one_or_none()


@login_manager.request_loader
def request_loader(req):
    form_data = req.form
    user = db.session.query(User).filter(db.and_(User.email == form_data.get("email"))).first()

    if user:
        password = form_data.get('password')

        if not password:
            return

        salt = user.salt
        secret_salt = current_app.config["SECRET_SALT"]
        password = hashlib.sha512((secret_salt + password + salt).encode()).hexdigest()

        luser = LoginUser(user, active=True, authenticated=password == user.password)
        login_user.is_authenticated = password == user.password
    else:
        return

    return luser


@urls.route("/login", methods=["GET"])
def login_form():
    return render_template('login.html', title='ログインページ｜JAEIS ポータル', message='')


@urls.route("/login", methods=["POST"])
def login():
    form_data = request.form
    user = db.session.query(User).filter(db.and_(User.email == form_data.get("email"))).first()

    if user:
        password = form_data.get('password')
        salt = user.salt
        secret_salt = current_app.config["SECRET_SALT"]
        password = hashlib.sha512((secret_salt + password + salt).encode()).hexdigest()
    else:
        return render_template('login.html', title='ログインページ｜JAEIS ポータル', message='ユーザIDもしくはパスワードが間違っています', alerts='alert-danger')

    if StateDefinition.CHANGE_PASSWORD.value == user.state:
        return render_template('login.html', title='ログインページ｜JAEIS ポータル', message='パスワードリセット手続き中です． メールに記載されたリンクからパスワード変更を行ってください', alerts='alert-warning')
    elif StateDefinition.ENABLE.value != user.state:
        return render_template('login.html', title='ログインページ｜JAEIS ポータル', message='アカウント認証が完了していません． メールに記載されたリンクから認証作業を行ってください', alerts='alert-warning')
    elif password != user.password:
        return render_template('login.html', title='ログインページ｜JAEIS ポータル', message='ユーザIDもしくはパスワードが間違っています', alerts='alert-danger')
    else:
        login_user(LoginUser(user))
        user_profile = db.session.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        # session['user_profile'] = user_profile

    return redirect(url_for("urls.home"))


@urls.route('/logout')
def logout():
    logout_user()
    session.pop('user_profile', None)
    return render_template('login.html', title='ログアウトページ｜JAEIS ポータル', message='ログアウトしました．', alerts='alert-success')


@urls.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template('signup_input.html', title='入力｜アカウント作成｜JAEIS ポータル')
    else:
        form_data = request.form
        return render_template('signup_input.html', title='確認｜アカウント作成｜JAEIS ポータル', form_data=form_data)


@urls.route("/signup-confirm", methods=["POST"])
def signup_confirm():
    form_data = request.form
    count = db.session.query(User).filter_by(email=form_data.get('email1')).count()
    if count:
        return render_template('signup_invalid.html', title='確認｜アカウント作成｜JAEIS ポータル', form_data=form_data)
    else:
        return render_template('signup_confirm.html', title='確認｜アカウント作成｜JAEIS ポータル', form_data=form_data)


@urls.route("/signup-complete", methods=["POST"])
def signup_complete():
    # リクエストからformデータを取得
    form_data = request.form
    # 2重登録防止
    count = db.session.query(User).filter_by(email=form_data.get('email1')).count()
    if count:
        return render_template('signup_invalid.html', title='確認｜アカウント作成｜JAEIS ポータル', form_data=form_data)

    # 認証トークン
    token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(24)])

    # 権限（Memberで固定）
    role = RoleDefinition.MEMBER.value

    # アカウントの状態（Signup状態で固定）
    state = StateDefinition.SIGNUP.value

    # パスワードをハッシュ化
    password = form_data.get('password1')
    salt = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])
    secret_salt = current_app.config["SECRET_SALT"]
    password = hashlib.sha512((secret_salt + password + salt).encode()).hexdigest()
    member_type = db.session.query(MemberType).filter_by(label=form_data.get('member')).first()
    address_type = db.session.query(AddressType).filter_by(label=form_data.get('address_type')).first()

    user = User(name="", email=form_data.get('email1'), password=password, member_id='', member_type_id=member_type.id, member_validate=False,
                salt=salt, role=role, state=state, token=token,
                token_period=datetime.now(JST) + timedelta(days=1))
    db.session.add(user)
    db.session.flush()

    user_profile = UserProfile(user_id=user.id,
                               first_name=form_data.get('firstName'), last_name=form_data.get('lastName'),
                               first_name_kana=form_data.get('firstNameKana'), last_name_kana=form_data.get('lastNameKana'),
                               first_name_roman=form_data.get('firstNameRoman'), last_name_roman=form_data.get('lastNameRoman'),
                               organization=form_data.get('organization'), department=form_data.get('department'), address_type_id=address_type.id,
                               zip=form_data.get('zip01'), prefecture=form_data.get('pref01'), municipalities=form_data.get('addr01'),
                               address1=form_data.get('addr02'), address2=form_data.get('addr03'), phone=form_data.get('phone'))
    db.session.add(user_profile)
    db.session.commit()

    subject = "JAEIS マイページ アカウント認証"
    body = f"""{form_data.get('lastName')} {form_data.get('firstName')} 様
           
JAEIS全国大会参加登録ページのアカウント申請を受け付けました．
下記のURLをクリックして登録を完了してください．
{request.host_url}authenticate?token={token}

認証手続きが完了しましたら，このメールは削除してもかまいません．
認証手続きの有効期限は24時間です．
不具合，不明な点がございましたら下記までご連絡願います．

--
日本情報科教育学会 全国大会実行委員会
Email: taikai@jaeis-org.sakura.ne.jp
"""
    msg = Message(recipients=[form_data.get('email1')], body=body, subject=subject)
    mail.send(msg)

    return render_template('signup_complete.html', title='完了｜アカウント作成｜JAEIS ポータル')


@urls.route("/authenticate")
def authenticate():
    token = request.args.get('token', default='', type=str)
    user = db.session.query(User).filter(
        db.and_(User.token == token, User.state == StateDefinition.SIGNUP.value, User.token_period >= datetime.now(JST))).first()
    if user:
        user.state = StateDefinition.ENABLE.value
        user.token = ''
        user.token_period = None
        user.updated_at = datetime.now(JST)

        db.session.add(user)
        db.session.commit()

        return render_template('authenticate_success.html', title='アカウント認証｜JAEIS ポータル')
    else:
        return render_template('authenticate_failure.html', title='アカウント認証｜JAEIS ポータル')


@urls.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template('reset_password.html', title='パスワードリセット｜JAEIS ポータル', alerts="alert-light", message="アカウント作成時に登録したメールアドレスを入力してください．")
    else:
        token = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(36)])
        user = db.session.query(User).filter(User.email == request.form.get('email')).first()

        if not user:
            return render_template('reset_password.html', title='パスワードリセット｜JAEIS ポータル', alerts="alert-warning", message="入力されたメールアドレスは登録されていません．")

        user.state = StateDefinition.CHANGE_PASSWORD.value
        user.token = token
        user.token_period = datetime.now(JST) + timedelta(days=1)
        user.updated_at = datetime.now(JST)

        db.session.add(user)
        db.session.commit()

        subject = "JAEIS 全国大会参加登録ページ パスワードリセット"
        body = f"""JAEIS全国大会参加登録ページのパスワードリセット申請を受け付けました．
下記のURLをクリックしてパスワードリセットを完了してください．
{request.host_url}change-password?token={token}
このリンクの有効期限は24時間です．

新しいパスワードリセットリンクを取得するには，
{request.host_url}reset-password
にアクセスしてください．

不具合，不明な点がございましたら下記までご連絡願います．

--
日本情報科教育学会 全国大会実行委員会
Email: taikai@jaeis-org.sakura.ne.jp
"""
        msg = Message(recipients=[request.form.get('email')], body=body, subject=subject)
        mail.send(msg)

        return render_template('reset_password.html', title='パスワードリセット｜JAEIS ポータル', state="send-link", alerts="alert-success", message="パスワードリセット用リンクを送信しました．")


@urls.route("/change-password", methods=["GET", "POST"])
def change_password():
    if request.method == "GET":
        token = request.args.get('token', default='', type=str)
        user = db.session.query(User).filter(
            db.and_(User.token == token, User.state == StateDefinition.CHANGE_PASSWORD.value, User.token_period >= datetime.now(JST))).first()
        if user:
            return render_template('change_password.html', title='パスワード変更｜JAEIS ポータル', user=user)
        else:
            return render_template('change_password.html', title='パスワード変更｜JAEIS ポータル', alerts="alert-warning",
                                   message="パスワードリセットに失敗しているか，URLの有効期限が切れている可能性があります．")
    else:
        user = db.session.query(User).filter(
            db.and_(User.email == request.form.get('email'), User.state == StateDefinition.CHANGE_PASSWORD.value,
                    User.token_period >= datetime.now(JST))).first()

        if user:

            salt = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(32)])
            secret_salt = current_app.config["SECRET_SALT"]

            user.password = hashlib.sha512((secret_salt + request.form.get('password1') + salt).encode()).hexdigest()
            user.salt = salt
            user.state = StateDefinition.ENABLE.value
            user.token = ''
            user.token_period = None
            user.updated_at = datetime.now(JST)

            db.session.add(user)
            db.session.commit()

            return render_template('change_password.html', title='パスワード変更｜JAEIS ポータル', state="change-password-success", alerts="alert-success",
                                   message="パスワードを変更しました．")

        else:
            return render_template('change_password.html', title='パスワード変更｜JAEIS ポータル', alerts="alert-warning",
                                   message="パスワードリセットに失敗しているか，URLの有効期限が切れている可能性があります．")


@urls.route("/home")
@login_required
def home():
    _login_user = load_user(current_user.id)
    return render_template('home.html', title='マイページ｜JAEIS ポータル', login_user=_login_user)


@urls.route("/event/list")
@login_required
def get_event_list():
    _login_user = load_user(current_user.id)
    event_list = db.session.query(Event).order_by(Event.created_at.desc()).all()
    event_attend_user_list = []
    for event in event_list:
        event_attend_user = db.session.query(EventAttendUser).filter(
            db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id, EventAttendUser.cancel.is_(False))).first()

        presentation = db.session.query(Presentation).filter(db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).first()

        if event.date[-1] < datetime.now():
            is_attend_timeout = True
        else:
            is_attend_timeout = False

        if event.attend_period < datetime.now():
            is_pre_attend_timeout = True
        else:
            is_pre_attend_timeout = False

        if event.presenting_papers_period < datetime.now():
            is_presenting_timeout = True
        else:
            is_presenting_timeout = False

        event_attend_user_list.append([event, event_attend_user, presentation, is_attend_timeout, is_pre_attend_timeout, is_presenting_timeout])
    print(event_attend_user_list)

    return render_template('event/list.html', title='大会・研究会一覧｜JAEIS ポータル', login_user=_login_user, event_attend_user_list=event_attend_user_list, message='')


@urls.route("/event/info", methods=["POST"])
@login_required
def event_info():
    _login_user = load_user(current_user.id)
    form_data = request.form

    event = db.session.query(Event).filter(Event.id == form_data.get('event_id')).first()
    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id)).first()
    fee = db.session.query(EventFee).filter(
        db.and_(EventFee.event_id == form_data.get('event_id'), EventFee.member_type_id == _login_user.member_type.id)).first()

    if event.date[0] < datetime.now():
        enable_get_receipt = True
    else:
        enable_get_receipt = False

    return render_template('event/info.html', title='大会・研究会 参加状況｜JAEIS ポータル', login_user=_login_user, event=event, event_attend_user=event_attend_user, fee=fee, enable_get_receipt=enable_get_receipt)


@urls.route("/event/getAttachment", methods=["POST"])
@login_required
def event_get_attachment():
    form_data = request.form
    event = db.session.query(Event).filter(Event.id == form_data.get('event_id')).first()

    path = "webapp/attachment/event/" + str(event.id) + "/" + event.attachment_path
    mimetype = event.attachment_mimetype if event.attachment_mimetype else mimetypes.guess_type(event.attachment_path)[0]
    #
    # return send_file(path, as_attachment=True, mimetype=mimetype)

    response = make_response()
    response.data = open(path, "rb").read()
    response.headers['Content-Disposition'] = 'attachment; filename=' + event.attachment_path
    response.mimetype = mimetype

    return response


@urls.route("/event/attend", methods=["POST"])
@login_required
def event_attend():
    _login_user = load_user(current_user.id)
    # リクエストからformデータを取得
    form = request.form
    # 文字列の配列をDatetimeオブジェクトの配列に変換
    attend_date = [datetime.strptime(i, '%Y-%m-%d %H:%M:%S') for i in form.getlist('attend_date_list')]

    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_((EventAttendUser.user_id == current_user.id), EventAttendUser.event_id == form.get('event_id'))).first()

    if event_attend_user:
        event_attend_user.attend_date = attend_date
        event_attend_user.expect_papers = True if form.get('expect_papers') == 'True' else False
        event_attend_user.attend_social_gathering = True if form.getlist('attend_social_gathering') == 'True' else False
        event_attend_user.cancel = False
        event_attend_user.updated_at = datetime.now(JST)
    else:
        event_attend_user = EventAttendUser(user_id=current_user.id, event_id=form.get('event_id'), attend_date=attend_date,
                                            expect_papers=(True if form.get('expect_papers') == 'True' else False),
                                            attend_social_gathering=(True if form.getlist('attend_social_gathering') == 'True' else False),
                                            payment_status=PaymentStatusDefinition.UNCONFIRMED.value,
                                            created_at=datetime.now(JST))
    db.session.add(event_attend_user)
    db.session.commit()

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        Event.id == EventAttendUser.event_id).first()
    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id)).first()
    fee = db.session.query(EventFee).filter(
        db.and_(EventFee.event_id == form.get('event_id'), EventFee.member_type_id == _login_user.member_type.id)).first()

    return render_template('event/info.html', title='大会・研究会 参加状況｜JAEIS ポータル', login_user=_login_user, event=event, event_attend_user=event_attend_user, fee=fee,
                           message='参加申込を受付ました．')


@urls.route("/event/cancel", methods=["POST"])
@login_required
def event_cancel():
    _login_user = load_user(current_user.id)
    form = request.form
    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_((EventAttendUser.user_id == current_user.id), EventAttendUser.event_id == form.get('event_id'))).first()
    event_attend_user.cancel = True
    cancel_event_name = event_attend_user.event.name
    db.session.add(event_attend_user)
    db.session.commit()

    event_list = db.session.query(Event).order_by(Event.created_at.desc()).all()
    event_attend_user_list = []
    for event in event_list:
        event_attend_user = db.session.query(EventAttendUser).filter(
            db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id, EventAttendUser.cancel.is_(False))).first()
        presentation = db.session.query(Presentation).filter(
            db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).first()

        if event.date[-1] < datetime.now():
            is_attend_timeout = True
        else:
            is_attend_timeout = False

        if event.attend_period < datetime.now():
            is_pre_attend_timeout = True
        else:
            is_pre_attend_timeout = False

        if event.presenting_papers_period < datetime.now():
            is_presenting_timeout = True
        else:
            is_presenting_timeout = False

        event_attend_user_list.append([event, event_attend_user, presentation, is_attend_timeout, is_pre_attend_timeout, is_presenting_timeout])


    return render_template('event/list.html', title='大会・研究会一覧｜JAEIS ポータル', login_user=_login_user, event_list=event_list,
                           event_attend_user_list=event_attend_user_list, message=cancel_event_name + "の参加を取り消しました．")


@urls.route("/event/presentation/register/input", methods=["POST"])
@login_required
def event_presentation_register():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()

    return render_template('event/presentation_register_input.html', title='発表登録｜JAEIS ポータル', login_user=_login_user, event=event)


@urls.route("/event/presentation/change_co_author_num", methods=["POST"])
@login_required
def co_author_form():
    co_author_num = request.form.get('co_author_num')
    print(co_author_num)
    return render_template('co_author_form.html', title='発表登録｜JAEIS ポータル', co_author_num=int(co_author_num))


@urls.route("/event/presentation/register/confirm", methods=["POST"])
@login_required
def event_presentation_confirm():
    _login_user = load_user(current_user.id)
    form = request.form
    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()
    keyword_list = ','.join(form.getlist('keyword'))
    return render_template('event/presentation_register_confirm.html', title='発表登録｜JAEIS ポータル', login_user=_login_user, event=event, form=form,
                           keyword_list=keyword_list)


@urls.route("/event/presentation/register/complete", methods=["POST"])
@login_required
def event_presentation_complete():
    _login_user = load_user(current_user.id)
    form = request.form

    user_profile = db.session.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    user_profile.first_name_roman = form.get('firstNameRoman')
    user_profile.last_name_roman = form.get('lastNameRoman')
    db.session.add(user_profile)
    db.session.flush()

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()

    presentation = Presentation(user_id=current_user.id, event_id=event.id, type=form.get('presentation_type'), title=form.get('title'),
                                abstract=form.get('abstract'), keyword=form.get('keyword'), keyword_free=form.get('keyword-free'),
                                _copyright=form.get('copyright'), paper_status='原稿未提出', is_cancel=False)
    db.session.add(presentation)
    db.session.flush()

    for i in range(int(form.get('coAuthorNum'))):
        co_author = CoAuthor(member_id='', email='', first_name=form.get('firstName-' + str(i + 1)), last_name=form.get('lastName-' + str(i + 1)),
                             first_name_kana=form.get('firstNameKana-' + str(i + 1)), last_name_kana=form.get('lastNameKana-' + str(i + 1)),
                             first_name_roman=form.get('firstNameRoman-' + str(i + 1)), last_name_roman=form.get('lastNameRoman-' + str(i + 1)),
                             organization=form.get('organization-' + str(i + 1)), department=form.get('department-' + str(i + 1)))

        db.session.add(co_author)
        db.session.flush()

        presentation_co_author = PresentationCoAuthor(presentation_id=presentation.id, co_author_id=co_author.id)
        db.session.add(presentation_co_author)
        db.session.flush()

    db.session.commit()

    presentation_list = db.session.query(Presentation).filter(db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).all()

    return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user, event=event, presentation_list=presentation_list, message='発表申込が完了しました．', alert='alert-success')


@urls.route("/event/presentation/list", methods=["POST"])
@login_required
def event_presentation_list():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()

    presentation_list = db.session.query(Presentation).filter(db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).order_by(Presentation.id.asc()).all()

    return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user, event=event,
                           presentation_list=presentation_list)


@urls.route("/event/presentation/cancel", methods=["POST"])
@login_required
def event_presentation_cancel():
    _login_user = load_user(current_user.id)
    form = request.form

    presentation = db.session.query(Presentation).filter(Presentation.id == form.get('presentation_id')).first()
    presentation.is_cancel = True
    db.session.add(presentation)
    db.session.flush()

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()

    presentation_list = db.session.query(Presentation).filter(db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).order_by(Presentation.id.asc()).all()

    db.session.commit()

    return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user,
                           event=event, presentation_list=presentation_list, message='1件の発表を取り消しました．', alert='alert-warning')


@urls.route("/event/presentation/upload-paper", methods=["POST"])
@login_required
def event_presentation_upload_paper():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).join(EventForm, Event.event_form_id == EventForm.id).outerjoin(
        EventAttendUser,
        db.and_(Event.id == EventAttendUser.event_id, EventAttendUser.user_id == current_user.id)).first()

    presentation_list = db.session.query(Presentation).filter(db.and_(Presentation.event_id == event.id, Presentation.user_id == current_user.id, Presentation.is_cancel.is_(False))).order_by(Presentation.id.asc()).all()

    if 'inputFile' not in request.files:
        flash('No file part')
        return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user,
                               event=event, presentation_list=presentation_list, message='リクエストにファイルパートが含まれていません．', alert='alert-danger')

    file = request.files['inputFile']
    file_name = file.filename
    if '' == file_name:
        flash('No selected file')
        return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user,
                               event=event, presentation_list=presentation_list, message='ファイルが選択されていません．', alert='alert-danger')

    print('eventId', form.get('event_id'))
    print(request.files)
    print('presentationId', form.get('presentation_id'))

    app_root = os.path.dirname(os.path.abspath(__file__))
    upload_folder = 'uploads/papers/events/' + str(event.id)
    os.makedirs(os.path.join(app_root, upload_folder), exist_ok=True)

    upload_file_name = str(current_user.id) + '-' + str(form.get('presentation_id')) + '.pdf'
    file.save(os.path.join(app_root, upload_folder, upload_file_name))

    presentation = db.session.query(Presentation).filter(Presentation.id == form.get('presentation_id')).first()
    presentation.paper_status = '原稿提出済み'
    db.session.add(presentation)
    db.session.commit()

    return render_template('event/presentation_list.html', title='発表一覧｜JAEIS ポータル', login_user=_login_user, event=event,
                           presentation_list=presentation_list, message='原稿をアップロードしました．', alert='alert-success')


@urls.route("/event/get-receipt", methods=["POST"])
@login_required
def get_receipt():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).first()
    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id)).first()
    fee = db.session.query(EventFee).filter(
        db.and_(EventFee.event_id == form.get('event_id'), EventFee.member_type_id == _login_user.member_type.id)).first()

    pdf_title = "receipt"

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'enable-local-file-access': "",
    }

    #Blueprintを使っているのでcuurent_appで取得する
    template = current_app.jinja_env.get_template('event/receipt.html')
    #Falseはファイルを作成しないでストリームにするフラグ
    pdf_buf = pdfkit.from_string(template.render(title='領収書｜JAEIS ポータル', login_user=_login_user, event=event, event_attend_user=event_attend_user, fee=fee), False, options=options)

    response = make_response(pdf_buf)
    dispostion = "attachment; filename*=UTF-8''"
    #日本語をUrlエンコード
    dispostion += urllib.parse.quote(pdf_title + '.pdf')
    response.headers['Content-Disposition'] = dispostion
    response.mimetype = 'application/pdf'

    return response


    # return render_template('event/receipt.html', title='領収書｜JAEIS ポータル', login_user=_login_user)


@urls.route("/event/input-receipt-addressed", methods=["POST"])
@login_required
def input_receipt_addressed():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).first()
    event_attend_user = db.session.query(EventAttendUser).filter(
        db.and_(EventAttendUser.event_id == event.id, EventAttendUser.user_id == current_user.id)).first()
    fee = db.session.query(EventFee).filter(
        db.and_(EventFee.event_id == form.get('event_id'), EventFee.member_type_id == _login_user.member_type.id)).first()

    event_attend_user.receipt_addressed = form.get('receiptAddressed')
    db.session.add(event_attend_user)
    db.session.commit()

    return render_template('event/info.html', title='大会・研究会 参加状況｜JAEIS ポータル', login_user=_login_user, event=event, event_attend_user=event_attend_user, fee=fee)


@urls.route("/event/attendance-list", methods=["POST"])
@login_required
def event_attendance_list():
    _login_user = load_user(current_user.id)
    form = request.form

    event_attend_user_list = db.session.query(EventAttendUser).filter(EventAttendUser.event_id == form.get('event_id')).order_by(EventAttendUser.user_id.asc())
    # print('参加者リスト', event_attend_user_list)
    #
    # for event_attend_user in event_attend_user_list:
    #     print('event_attend_user', event_attend_user.user.user_profile.first_name)

    return render_template('event/attendance_list.html', title='参加者リスト', login_user=_login_user, event_id=form.get('event_id'), event_attend_user_list=event_attend_user_list)


@urls.route("/event/change-payment-status", methods=["POST"])
@login_required
def event_change_payment_status():
    _login_user = load_user(current_user.id)
    form = request.form

    event_attend_user = db.session.query(EventAttendUser).filter(db.and_(EventAttendUser.user_id == form.get('user_id'), EventAttendUser.event_id == form.get('event_id'))).first()
    # print('参加者リスト', event_attend_user_list)
    #
    # for event_attend_user in event_attend_user_list:
    #     print('event_attend_user', event_attend_user.user.user_profile.first_name)
    if strtobool(form.get('checked')):
        event_attend_user.payment_status = '振込確認済み'
    else:
        event_attend_user.payment_status = '振込未確認'

    db.session.add(event_attend_user)
    db.session.commit()

    # print(form.get('checked'))
    # print(form.get('event_id'))
    # print('event_attend_user', event_attend_user.user_id)

    return jsonify(form.get('user_id'), form.get('event_id'), form.get('checked'))


@urls.route("/event/getAttachment", methods=["POST"])
@login_required
def get_attachment():
    _login_user = load_user(current_user.id)
    form = request.form

    event = db.session.query(Event).filter(Event.id == form.get('event_id')).first()

    filename = event.attachment_path
    filepath = './webapp/attachement/event/' + event.id + '/' + filename

    return send_file(filepath, as_attachment=True, attachment_filename=filename, mimetype=event.attachment_mimetype)