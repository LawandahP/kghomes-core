
from config.celery import app as celery_task
from utils.utils import logger as serverLogger
from celery.utils.log import get_task_logger

from django_celery_beat.models import CrontabSchedule, PeriodicTask
celeryLogger = get_task_logger(__name__)



def createBill(lease):
    pass
    



@celery_task.task(name="send_activation_email_task")
def createRecurringBill():
    serverLogger.info("Created recurring Bill")
    celeryLogger.info("Created recurring Bill")

    # send_activation_email(data)









