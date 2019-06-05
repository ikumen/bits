from flask_github import GitHub
from backend import user


github = GitHub()

def init_app(app):
    """Initialize any third party support"""
    github.init_app(app)
    github.access_token_getter(lambda: user.repository.get(app.config.get('GITHUB_USER_ID'))['access_token'])


