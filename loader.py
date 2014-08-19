import inspect
import importlib
import random
from path import path
from celery.utils.log import get_task_logger

import services

email_services = []
logger = get_task_logger(__name__)


def __load_email_services():
    """
    Loads all the modules within the service module and finds classes that are
    a subclass of BaseService. Creates a list of email services.
    """
    if email_services:
        return
    service_dir = path('services')
    for f in service_dir.files():
        if f.endswith('.py'):
            module_name = f.splitext()[0].replace('/', '.')
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                logger.debug("Failed to load %s" % f)
                continue
            classes = inspect.getmembers(module, inspect.isclass)
            for cls_name, cls_object in classes:
                if (issubclass(cls_object, services.BaseService) and
                   not inspect.isabstract(cls_object)):
                    email_services.append(cls_object)


def get_random_email_service():
    """
    Gives an random emial service object. This method returns the instantiated
    object.
    """
    __load_email_services()
    if not email_services:
        return None
    email_service_class = random.choice(email_services)
    return email_service_class()
