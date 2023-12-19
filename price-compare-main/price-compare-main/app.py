from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
def create_app(config_class=Config):
    app = Flask(__name__) # creates the Flask instance, __name__ is the name of the current Python module
    app.config.from_object(config_class)

    app.config['SECRET_KEY'] = 'secret-key-goes-here' # it is used by Flask and extensions to keep data safe
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # deactivate Flask-SQLAlchemy track modifications
    app.config['SQLALCHEMY_POOL_SIZE'] = 100
    # app.config['SQLALCHEMY_POOL_TIMEOUT'] = 10
    # app.config['SQLALCHEMY_POOL_PRE_PING'] = True
    # app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280, "pool_timeout": 10, "pool_pre_ping": True}

    db.init_app(app) # Initialiaze sqlite database
    migrate = Migrate(app, db)
    
    # The login manager contains the code that lets your application and Flask-Login work together
    login_manager = LoginManager() # Create a Login Manager instance
    login_manager.login_view = 'auth.login' # define the redirection path when login required and we attempt to access without being logged in
    # login_manager.logout_view = 'auth.logout' # define the redirection path when login required and we attempt to access without being logged in
    login_manager.init_app(app) # configure it for login
    
    from models import User
    @login_manager.user_loader
    def load_user(user_id): #reload user object from the user ID stored in the session
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    # blueprint for auth routes in our app
    # blueprint allow you to orgnize your flask app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app