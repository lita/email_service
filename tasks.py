from celery import Celery
from celery.utils.log import get_task_logger
from validate_email import validate_email


import loader
from services import MissingSender, MissingRecipient
from services import EmailServiceResponseException

app = Celery('tasks', config_source='celeryconfig')
logger = get_task_logger(__name__)


@app.task(bind=True)
def send_mail(self, email_dict):
    emails, bad_emails = validate_emails(email_dict["to"])
    if not emails or not validate_email(email_dict["from_email"]):
        return "Email wasn't formatted properly."
    email_dict["to"] = emails
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

    result = "Using %s, sent to %s." % (email_service.name, ", ".join(emails))
    if bad_emails:
        result += "Falied to send to %s" % ", ".join(bad_emails)
    return result


def validate_emails(emails_to_parse):
    emails, bad_emails = [], []
    for email in emails_to_parse.split(','):
        email = email.strip()
        target = emails if validate_email(email) else bad_emails
        target.append(email)
    return emails, bad_emails
