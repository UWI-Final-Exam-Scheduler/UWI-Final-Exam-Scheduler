import pytest
from App.controllers.admin import create_admin
from App.models.admin import Admin
from App.database import db

def test_create_admin(empty_db):
	admin = create_admin('adminuser', 'securepass')
	assert isinstance(admin, Admin)
	assert admin.username == 'adminuser'
	assert admin.role == 'admin'
	# Check DB persistence
	found = Admin.query.filter_by(username='adminuser').first()
	assert found is not None
	assert found.username == 'adminuser'
