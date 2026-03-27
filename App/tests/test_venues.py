import pytest
from App.controllers.venue import create_venue, get_venue_by_name

def test_create_venue_success(empty_db):
    venue = create_venue("Room A", 100)
    assert venue.name == "Room A"
    assert venue.capacity == 100

def test_get_venue_by_name_not_found(empty_db):
    result = get_venue_by_name("Room A")
    assert result == "Venue with name Room A not found."