from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:123456@localhost/BDDentista'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers import main_bp
    app.register_blueprint(main_bp)

    return app
