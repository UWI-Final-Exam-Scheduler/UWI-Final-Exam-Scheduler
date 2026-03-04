# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .admin import setup_admin
from .courses import course_views
from .venues import venue_views

views = [user_views, index_views, auth_views, course_views, venue_views] 
# blueprints must be added to this list