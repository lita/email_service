from celery import Celery
from celery.utils.log import get_task_logger


import loader
from services import MissingSender, MissingRecipient
from services import EmailServiceResponseException

app = Celery('tasks', config_source='celeryconfig')
logger = get_task_logger(__name__)


@app.task(bind=True)
def send_mail(self, email_dict):
    emails = email_dict['to']
    email_dict['to'] = [email.strip() for email in emails.split(',')]
    email_service = loader.get_random_email_service()
    logger.info("Got %s email service" % email_service.name)
    try:
        logger.debug("Trying to sending email")
        email_service.send(**email_dict)
    except (MissingSender, MissingRecipient) as err:
        logger.debug("Failed. Missing sender or recipient email address.")
        raise err
    except EmailServiceResponseException as exc:
        logger.debug("Failed. Got a response error. Trying again...")
        raise self.retry(exc=exc)

    return email_service.name
