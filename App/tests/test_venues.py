import pytest
from App.controllers.venue import import_venues_from_csv, get_all_venues, get_venue_by_name
from App.models import Venue
from App.database import db

def test_import_venues_success(empty_db, tmp_path):
    csv_content = """Venue Name,Capacity\nRoom A,100\nRoom B,200\n"""
    csv_file = tmp_path / "venues.csv"
    csv_file.write_text(csv_content)

    msg = import_venues_from_csv(str(csv_file))
    assert "Added 2 new venues" in msg
    assert "Skipped 0 existing venues" in msg
    venues = Venue.query.all()
    assert len(venues) == 2
    assert set([v.name for v in venues]) == {"Room A", "Room B"}
    assert set([v.capacity for v in venues]) == {100, 200}

def test_import_venues_duplicate(empty_db, tmp_path):
    csv_content = """Venue Name,Capacity\nRoom A,100\n"""
    csv_file = tmp_path / "venues.csv"
    csv_file.write_text(csv_content)
    import_venues_from_csv(str(csv_file))
    msg = import_venues_from_csv(str(csv_file))
    assert "Added 0 new venues" in msg
    assert "Skipped 1 existing venues" in msg

def test_import_venues_invalid_row(empty_db, tmp_path):
    csv_content = """Venue Name,Capacity\n,100\n"""
    csv_file = tmp_path / "venues.csv"
    csv_file.write_text(csv_content)
    with pytest.raises(ValueError):
        import_venues_from_csv(str(csv_file))

def test_get_all_venues_empty(empty_db):
    assert get_all_venues() == []

def test_get_all_venues_with_venues(empty_db):
    v1 = Venue(name="Room X", capacity=50)
    v2 = Venue(name="Room Y", capacity=75)
    db.session.add_all([v1, v2])
    db.session.commit()
    venues = get_all_venues()
    assert len(venues) == 2
    names = {v['name'] for v in venues}
    capacities = {v['capacity'] for v in venues}
    assert names == {"Room X", "Room Y"}
    assert capacities == {50, 75}

def test_get_venue_by_name_found(empty_db):
    v = Venue(name="Special Room", capacity=123)
    db.session.add(v)
    db.session.commit()
    result = get_venue_by_name("Special Room")
    assert isinstance(result, dict)
    assert result['name'] == "Special Room"
    assert result['capacity'] == 123

def test_get_venue_by_name_not_found(empty_db):
    result = get_venue_by_name("Nonexistent Room")
    assert isinstance(result, str)
    assert "not found" in result