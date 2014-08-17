import json
import unittest
from mock import patch

from services import mandrill, mailgun
from services import EmailServiceResponseException


class FakeResponse(object):

    def __init__(self, code, text):
        self.status_code = code
        self.text = text

    def ok(self):
        return self.status_code == 200


class FakeSession(object):

    def __init__(self):
        self.__session.auth = None

    def post(url, data=None):
        pass


class TestMandrill(unittest.TestCase):

    def setUp(self):
        self.mandrill = mandrill.MandrillService()
        mandrill.api_key = "this is a dummy"

    @patch("services.mandrill.requests")
    def test_ping(self, mock):
        mock.post.return_value = FakeResponse(200, "PONG")
        result = self.mandrill.ping()
        self.assertEquals(result, "PONG")

    @patch("services.mandrill.requests")
    def test_ping_error(self, mock):
        mock.post.return_value = FakeResponse(404, "Bad Request")
        self.assertRaises(EmailServiceResponseException, self.mandrill.ping)

    @patch("services.mandrill.requests")
    def test_send(self, mock):
        mock.post.return_value = FakeResponse(200, "Sent")
        message = {
            'to': ['sender@example.com'],
            'from_email': 'fake@example.com',
            'subject': 'test',
            'text': 'This is a message'
        }
        self.mandrill.send(**message)
        expected = {
            'key': 'this is a dummy',
            'message': {
                'from_email': 'fake@example.com',
                'to': [{'email': 'sender@example.com'}],
                'subject': 'test',
                'text': 'This is a message'
            }
        }
        mock.post.assert_called_with(mandrill.url + '/messages/send',
                                     data=json.dumps(expected))


class TestMailgunService(unittest.TestCase):

    def setUp(self):
        self.api_key = "This is also fake"
        self.mailgun = mailgun.MailgunService()
        self.mailgun.api_key = "Fake Stuff"

    @patch.object(mailgun.requests.Session, "post")
    def test_ping(self, mock):
        mock.post.return_value = FakeResponse(200, "PONG")
        result = self.mailgun.ping()
        self.assertEquals(result, "PONG")
