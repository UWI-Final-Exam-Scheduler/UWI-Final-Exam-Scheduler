from App.database import db

class UserPreference(db.Model):
    __tablename__ = 'user_preference'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, nullable=False)
    abs_threshold = db.Column(db.Integer, nullable=False, default=5)
    perc_threshold = db.Column(db.Float, nullable=False, default=0.10)
    update_time = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())


    user = db.relationship('User', backref=db.backref('user_preference', uselist=False))

    def __init__(self, user_id, abs_threshold=5, perc_threshold=0.10):
        self.user_id = user_id
        self.abs_threshold = abs_threshold
        self.perc_threshold = perc_threshold