from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from server import api, frontend

app = DispatcherMiddleware(frontend.create_app(), {
        '/api': api.create_app()
    })

if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True)    