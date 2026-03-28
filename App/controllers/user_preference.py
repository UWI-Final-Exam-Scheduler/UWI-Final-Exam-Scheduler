from App.database import db
from App.models.user_preference import UserPreference

def get_user_preferences(user_id):
    preferences = UserPreference.query.filter_by(user_id=user_id).first()
    if not preferences:
        return None
    return {
        "abs_threshold": preferences.abs_threshold,
        "perc_threshold": preferences.perc_threshold
    }

def update_user_preferences(user_id, abs_threshold=None, perc_threshold=None):
    preferences = UserPreference.query.filter_by(user_id=user_id).first()

    if not preferences:
        preferences = UserPreference(user_id=user_id)
        db.session.add(preferences)

    if abs_threshold is not None:
        preferences.abs_threshold = abs_threshold

    if perc_threshold is not None:
        preferences.perc_threshold = perc_threshold
    
    db.session.commit()
    return {
        "abs_threshold": preferences.abs_threshold,
        "perc_threshold": preferences.perc_threshold
    }