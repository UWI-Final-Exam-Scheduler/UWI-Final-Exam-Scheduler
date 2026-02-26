import os
from datetime import timedelta

POSTGRES_SCHEME = 'postgres://'
POSTGRESQL_SCHEME = 'postgresql://'

def load_config(app, overrides):
    if os.path.exists(os.path.join('./App', 'custom_config.py')):
        app.config.from_object('App.custom_config')
    else:
        app.config.from_object('App.default_config')

    # Select Neon DB URI based on ENV
    env = os.environ.get('ENV', 'development')
    if env == 'production':
        db_url = os.environ.get('DATABASE_URI_NEON_PROD')
    else:
        db_url = os.environ.get('DATABASE_URI_NEON_DEV')
    
    if db_url:
        if db_url.startswith(POSTGRES_SCHEME):
            db_url = db_url.replace(POSTGRES_SCHEME, POSTGRESQL_SCHEME, 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        print(f"Using database URI: {db_url}")
    else:
        print("Warning: No database URI configured")

    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"

    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    
    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'

    for key in overrides:
        app.config[key] = overrides[key]