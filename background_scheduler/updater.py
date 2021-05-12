from apscheduler.schedulers.background import BackgroundScheduler


def start():
    """
        bgs is the name of the BackgroundScheduler object we will
        use for running jobs on the system. This will run no matter
        what time of day it is without needing any direct contact.
    """
    from travel.send_daily_email_reminder import send_daily_email_reminder
    bgs = BackgroundScheduler(daemon=True)
    # Job 1: send an email at 10:30:00
    bgs.add_job(send_daily_email_reminder, 'cron', hour=10, minute=30)
    bgs.start()
