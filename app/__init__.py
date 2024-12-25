from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/BDDentista'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers import main_bp
    app.register_blueprint(main_bp)

    return app
