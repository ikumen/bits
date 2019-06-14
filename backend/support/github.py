from flask_github import GitHub


github = GitHub()

def init_app(app, token_getter):
    """Initialize any third party support"""
    github.init_app(app)
    github.access_token_getter(token_getter)


