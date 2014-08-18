import os
import requests

from services import BaseService
from services import EmailServiceResponseException, MissingEnvironments


class MailgunService(BaseService):

    def __init__(self):
        self.initalize_and_format_domain_and_url()
        self.__session = requests.Session()
        self.__session.auth = ('api', self.api_key)
        self._name = "Mailgun"
        self.domain

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def initalize_and_format_domain_and_url(self):
        self.url = os.environ.get("MAILGUN_API_URL")
        self.api_key = os.environ.get("MAILGUN_API_KEY")
        domain = os.environ.get("MAILGUN_DOMAIN")
        if self.url and self.api_key and domain:
            domain = domain.strip("/")
            domain = domain.replace("https://", "").replace("http://", "")
            self.domain = domain
        else:
            raise MissingEnvironments(("Mailgun: Either MAILGUN_API_URL, "
                                       "MAILGUN_API_URL and/or MAILGUN_DOMAIN "
                                       "are not set in your environments"))

    def ping(self):
        resp = self.__session.get("%s/domains/%s" % (self.url, self.domain))
        if resp.status_code == 200:
            return "PONG"
        else:
            raise EmailServiceResponseException(resp.status_code,
                                                resp.text,
                                                self.name)

    def send(self, to=None, from_email=None, subject='', text='', **kwargs):
        self._validate_email(to, from_email)
        if not text:
            text = "Sent by Mailgun"
        msg = {
            'from': from_email,
            'to': to,
            'subject': subject,
            'text': text
        }
        url = "%s/%s/messages" % (self.url, self.domain)
        resp = self.__session.post(url, data=msg)
        if resp.ok:
            return True
        else:
            raise EmailServiceResponseException(resp.status_code,
                                                resp.text,
                                                self.name)
