import requests
import json

import config
from services import BaseService
from services import EmailServiceException, EmailServiceResponseException

url = config.MANDRILL_API_URL
api_key = config.MANDRILL_API_KEY


class MandrillService(BaseService):

    def __init__(self):
        self._name = "Mandrill"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def ping(self):
        data = {'key': api_key}
        resp = requests.post(url + '/users/ping', data=json.dumps(data))
        if resp.status_code == 200:
            return resp.text
        else:
            raise EmailServiceResponseException(resp.status_code,
                                                resp.text, self.name)

    def send(self, to=None, from_email=None, subject='', text='', **kwargs):
        self._validate_email(to, from_email)
        to = [{'email': email} for email in to]
        msg = {
            'from_email': from_email,
            'to': to,
            'subject': subject,
            'text': text
        }
        req = {
            'key': api_key,
            'message': msg
        }
        resp = requests.post(url + '/messages/send', data=json.dumps(req))
        if resp.ok:
            return True
        raise self.create_exception(resp)

    def create_exception(self, response):
        try:
            obj = response.json()
            execption_class = type(obj['name'].encode(),
                                   (EmailServiceResponseException,), {})
            return execption_class(response.status_code, obj['message'])
        except KeyError:
            return EmailServiceException(response.status_code,
                                         response.text, self.name)

