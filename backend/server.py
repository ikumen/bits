import time

from concurrent import futures
#from werkzeug.serving import run_simple
#from apscheduler.schedulers.background import BackgroundScheduler
from backend import create_app, Bits


app = create_app()


if __name__ == '__main__':
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(bits.upload_updates_to_github, 'interval', seconds=180)
    #scheduler.start()
    try:
        #run_simple('0.0.0.0', 5000, app, use_reloader=True, use_debugger=True)
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        #scheduler.shutdown()
        pass
