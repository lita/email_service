from abc import ABCMeta, abstractmethod, abstractproperty

"""
This contains the base class to interface between different email APIs.
Developers can subclass the BaseService class to add their own custom
interfaces, and the 'loader' module will be able to detect them, as long as
they live within the 'services' module and they are just one '.py' file.

Developers can store global settings in the environment variables. 
Feel free to look 'mandrill' and 'mailbox' as examples.
"""

class BaseService:
    """
    This is the base class for all the service classes.
    """

    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractmethod
    def ping(self):
        pass

    @abstractmethod
    def send(self, to=None, from_email=None, subject='', text='',
             cc=None, bcc=None, *args):
        pass

    def _validate_email(self, to, from_email):
        if not to:
            raise MissingSender("I don't know who to send your email to!")
        if not from_email:
            raise MissingRecipient(("I need to know who the email is from! "
                                    "Otherwise, it's creepy."))


class EmailServiceException(IOError):
    """This is a base exception for the email module."""
    pass


class EmailServiceResponseException(EmailServiceException):
    def __init__(self, code, msg, service_name="BaseService"):
        self.resp_code = code
        self.resp_error = msg
        self.service_name = service_name
        self.args = ("Response Status %d" % code, service_name, msg)


class MissingEnvironments(EmailServiceException):
    pass


class MissingSender(EmailServiceException):
    pass


class MissingRecipient(EmailServiceException):
    pass
