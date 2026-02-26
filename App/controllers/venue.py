from App.models import Venue
from App.database import db
import csv

def create_venue(name, capacity):
    newvenue = Venue(name=name, capacity=capacity)
    db.session.add(newvenue)
    db.session.commit()
    return newvenue

def import_venues_from_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)               
        for row in reader:
            if not row.get("Venue Name") or not row.get("Capacity"):
                raise ValueError(f"Missing required fields in row: {row}")
            
            name = str(row.get("Venue Name")).strip()
            capacity = int(row.get("Capacity"))

            existing = Venue.query.filter_by(name=name).first()
            if not existing:
                venue = Venue(name=name, capacity=capacity)
                db.session.add(venue)
        try:
            db.session.commit()    
        except Exception as e:
            db.session.rollback()
            raise e
        return "Venues imported successfully!"