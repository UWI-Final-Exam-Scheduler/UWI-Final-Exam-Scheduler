# FLASK_RUN_PORT=8080
# FLASK_APP=wsgi.py
# FLASK_DEBUG=True

# --- Flask ---
FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=e2625c620c2e6af070933da066608d85dcb23d1a2c7d3732f319288d42bcd9a1

# NeonDB connection
DATABASE_URI_NEON_DEV=postgresql://neondb_owner:npg_AzXyFdhR2Zq9@ep-raspy-firefly-ai7dfdm8-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DATABASE_URI_NEON_PROD=postgresql://neondb_owner:npg_AzXyFdhR2Zq9@ep-hidden-hall-ai5q2hdj-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# CORS / Frontend
FRONTEND_ORIGIN=http://localhost:3000