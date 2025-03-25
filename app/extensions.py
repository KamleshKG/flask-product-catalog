from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
session_store = Session()


def init_extensions(app):
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = "strong"

    limiter.init_app(app)
    session_store.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.token_loader
    def load_token(token):
        return User.verify_session_token(token)