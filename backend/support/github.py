from flask_github import GitHub
from backend.user import model as User


github = GitHub()

def init_app(app):
    """Initialize any third party support"""
    github.init_app(app)
    github.access_token_getter(lambda: User.get(app.config.get('GITHUB_USER_ID'))['access_token'])


