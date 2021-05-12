from apscheduler.schedulers.background import BackgroundScheduler
from travel.send_daily_email_reminder import *

def function():
    print('Printing stuff')

def start():
    sched = BackgroundScheduler()
    #sched.add_job(send_daily_email_reminder, "cron", hour=11, minute=36)
    sched.add_job(function, 'interval', seconds=5)
    sched.start()