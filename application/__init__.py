import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import click
from flask.cli import with_appcontext
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from flask import current_app

load_dotenv()

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .models import Employee, Opportunity, Comments
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    with app.app_context():
        db.create_all()
        create_database(app)
        update_db_schema(app)  # Call the schema update function here
        add_title_column_to_opportunity()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Employee.query.get(int(id))

    @app.cli.command("create-superuser")
    @click.option('--email', prompt=True)
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    @with_appcontext
    def create_superuser(email, password):
        """Creates a new superuser."""
        if Employee.query.filter((Employee.email == email)).first():
            print('A user with that username or email already exists.')
        else:
            new_user = Employee(email=email, password=password, role='admin')
            db.session.add(new_user)
            db.session.commit()
            print('Superuser created successfully.')

    return app

def create_database(app):
    if not os.path.exists('application/' + DB_NAME):
        db.create_all()
        print('Created Database!')


def update_db_schema(app):
    with app.app_context():
        connection = db.engine.connect()
        try:
            # Check if the 'role' column already exists
            result = connection.execute(text("PRAGMA table_info(employee);"))
            columns = [row[1] for row in result.fetchall()]  # Access 'name' column by index
            if 'role' not in columns:
                # Attempt to add the 'role' column if it does not exist
                sql_command = text("ALTER TABLE employee ADD COLUMN role VARCHAR(10) DEFAULT 'user';")
                connection.execute(sql_command)
        except OperationalError as e:
            print(f"OperationalError encountered: {e}")
        finally:
            connection.close()
            connection.close()
            

def add_title_column_to_opportunity():
    with current_app.app_context():
        connection = db.engine.connect()
        try:
            # Check if the 'title' column already exists in the 'opportunity' table to avoid errors
            result = connection.execute(text("PRAGMA table_info(Opportunity);"))
            columns = [row[1] for row in result.fetchall()]  # Access 'name' column by index
            if 'title' not in columns:
                # Attempt to add the 'title' column to the 'opportunity' table if it does not exist
                sql_command = text("ALTER TABLE Opportunity ADD COLUMN title VARCHAR(255);")
                connection.execute(sql_command)
                print("Column 'title' added to 'Opportunity' table successfully.")
        except Exception as e:
            print(f"Error encountered: {e}")
        finally:
            connection.close()