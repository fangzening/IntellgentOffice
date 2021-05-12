from django.apps import AppConfig
from .updater import *


class BackgroundSchedulerConfig(AppConfig):
    name = 'background_scheduler'

    def ready(self):
        start()
