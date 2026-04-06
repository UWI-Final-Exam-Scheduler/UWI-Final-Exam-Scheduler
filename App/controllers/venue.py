from App.models import Venue
from App.database import db
import csv

from App.models.exam import Exam

def create_venue(name, capacity):
    newvenue = Venue(name=name, capacity=capacity)
    db.session.add(newvenue)
    db.session.commit()
    return newvenue

def import_venues_from_csv(file_path):
    existing_venue_names = {
        name.lower() for (name,) in db.session.query(Venue.name).all()
    }
    inserted = 0
    skipped_existing = 0

    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if not row.get("Venue Name") or not row.get("Capacity"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            name = str(row.get("Venue Name")).strip()
            capacity = int(row.get("Capacity"))

            normalized_name = name.lower()
            if normalized_name in existing_venue_names:
                skipped_existing += 1
                continue

            venue = Venue(name=name, capacity=capacity)
            db.session.add(venue)
            existing_venue_names.add(normalized_name)
            inserted += 1
        try:
            db.session.commit()    
        except Exception as e:
            db.session.rollback()
            raise e
        return (
            f"Venues imported successfully! Added {inserted} new venues. "
            f"Skipped {skipped_existing} existing venues."
        )

def get_all_venues():
    venues = db.session.query(Venue).all()
    if not venues:
        return []
    venue_json = []
    for venue in venues:
        venue_json.append({
            "id": venue.id,
            "name": venue.name,
            "capacity": venue.capacity
        })
    return venue_json

def get_venue_by_name(name):
    venue = db.session.query(Venue).filter_by(name=name).first()
    if not venue:
        return f"Venue with name {name} not found."
    venue = {
        "id": venue.id,
        "name": venue.name,
        "capacity": venue.capacity
    }
    return venue

def get_venue_by_id(venue_id):
    venue = db.session.query(Venue).filter_by(id=venue_id).first()
    if not venue:
        return f"Venue with id {venue_id} not found."
    venue = {
        "id": venue.id,
        "name": venue.name,
        "capacity": venue.capacity
    }
    return venue

def get_exams_capacity_in_venue(venue_id:int, date:str, time:int):
    venue = get_venue_by_id(venue_id)
    if not venue:
        return "Venue not found."
    venue_exams = db.session.query(Exam).filter_by(venue_id=venue_id, date=date, time=time).all()
    for exam in venue_exams:
        print(f"Exam ID: {exam.id}, Course Code: {exam.courseCode}, Date: {exam.date}, Time: {exam.time}, Exam Length: {exam.exam_length}, Number of Students: {exam.number_of_students}")
