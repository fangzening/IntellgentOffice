from apscheduler.schedulers.background import BackgroundScheduler
from it_app.models import UserPasswordChange

bgs = BackgroundScheduler(daemon=True)


def password_change_expired(job_id, user, duration):
    UserPasswordChange.objects.get(user=user)


def generate_jobs(duration):
    bgs.add_job()
