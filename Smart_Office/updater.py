from apscheduler.schedulers.background import *


# This is a list of functions that will add jobs
def start_email_job():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(emailfunction, 'cron', day_of_week=0, hour=6)