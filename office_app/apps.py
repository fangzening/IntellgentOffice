from django.apps import AppConfig
# from apscheduler.schedulers.background import BackgroundScheduler
# from travel.send_daily_email_reminder import *
#
#
# class SmartOfficeAppConfig(AppConfig):
#     name = 'office_app'
#
#     @staticmethod
#     def start_jobs():
#         sched = BackgroundScheduler()
#         # sched.add_job(send_daily_email_reminder, "cron", hour=11, minute=36)
#         sched.add_job(print, 'interval', seconds=5, args=['Success'])
#         sched.start()
#
#     def ready(self):
#
#         self.start_jobs()


class SmartOfficeAppConfig(AppConfig):
    name = 'Smart_Office_App'
