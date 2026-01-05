"""
App-level settings for crm (mirrors Celery beat config present in project settings).
This file provides local access to Celery configuration if code prefers app-scoped settings.
"""
from celery.schedules import crontab

# Broker (fallback to Redis on localhost)
CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
