from App.models import Venue
from App.database import db

def create_venue(name, capacity):
    newvenue = Venue(name=name, capacity=capacity)
    db.session.add(newvenue)
    db.session.commit()
    return newvenue