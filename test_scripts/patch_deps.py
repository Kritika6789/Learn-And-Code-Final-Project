from server import models
def get_current_active_user():
    return models.User(id=4, username="man4", role="MANAGER")
def get_read_only_db():
    pass
