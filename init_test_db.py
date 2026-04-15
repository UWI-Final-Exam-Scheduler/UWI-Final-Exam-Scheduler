from App.database import db
from wsgi import app

if __name__ == "__main__":
    with app.app_context():
        print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
        db.create_all()
    print("test.db initialized with all tables.")