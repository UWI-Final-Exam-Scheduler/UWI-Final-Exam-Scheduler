import pytest
from App.controllers.user_preference import get_user_preferences, update_user_preferences
from App.models.user_preference import UserPreference
from App.database import db

def test_get_user_preferences_none(empty_db):
	assert get_user_preferences(1) is None

def test_update_user_preferences_create_and_get(empty_db):
	# Should create new preferences with defaults
	result = update_user_preferences(1)
	assert result["abs_threshold"] == 5
	assert result["perc_threshold"] == 0.10
	# Should retrieve the same
	prefs = get_user_preferences(1)
	assert prefs["abs_threshold"] == 5
	assert prefs["perc_threshold"] == 0.10

def test_update_user_preferences_update_values(empty_db):
	# Create with defaults
	update_user_preferences(2)
	# Update values
	result = update_user_preferences(2, abs_threshold=10, perc_threshold=0.25)
	assert result["abs_threshold"] == 10
	assert result["perc_threshold"] == 0.25
	# Retrieve and check
	prefs = get_user_preferences(2)
	assert prefs["abs_threshold"] == 10
	assert prefs["perc_threshold"] == 0.25
