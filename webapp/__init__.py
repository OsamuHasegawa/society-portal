from flask import Flask
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from webapp.database import db
from webapp.login_manager import login_manager
from webapp.mail import mail
from webapp.models.user import LoginUser
import webapp.models
from webapp.urls import urls


# def create_app():
app = Flask(__name__, instance_relative_config=True)

# print(app.url_map)
# print(app.config)

# CORS対応
# CORS(webapp)

# config読み込み
app.config.from_object('config.Config')
app.config.from_pyfile('config.cfg', silent=True)

# DB設定を読み込む
db.init_app(app)
migrate = Migrate(app, db)

# Mail設定を読み込む
mail.init_app(app)

# print(app.url_map)
# print(app.config)

login_manager.init_app(app)
login_manager.login_view = "urls.login"

# Blueprint関連
app.register_blueprint(urls)

# CSRF対応
csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    return LoginUser.query.filter(LoginUser.id == user_id).one_or_none()




#    return app


# app = create_app()
