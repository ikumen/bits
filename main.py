import time

from concurrent import futures
#from werkzeug.serving import run_simple
#from apscheduler.schedulers.background import BackgroundScheduler
from backend import create_app, Bits

app = create_app()
print('about to run')
if __name__ == '__main__':
    app.run(debug=True)
