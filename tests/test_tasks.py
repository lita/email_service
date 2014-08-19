import unittest
from mock import patch, Mock
from celery.exceptions import Retry

import tasks
from services import EmailServiceResponseException

class TestTasks(unittest.TestCase):
    def setUp(self):
        tasks.app.conf.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        tasks.app.conf.CELERY_ALWAYS_EAGER = False

    @patch('tasks.send_mail.retry')
    @patch('tasks.loader.get_random_email_service')
    def test_celery_send_email(self, mock_loader, mock_retry):
        form = {
            "to": "test@gmail.com",
            "from_email": "test@gmail.com",
            "subject": "thisi s a test",
            "text": "text"
        }
        mock = Mock()
        mock_loader.return_value = mock
        tasks.send_mail.delay(form)

        self.assertTrue(mock.send.call_count == 1)
        self.assertFalse(mock_retry.called)

    @patch('tasks.send_mail.retry')
    @patch('tasks.loader.get_random_email_service')
    def test_celery_send_retry(self, mock_loader, mock_retry):
        form = {
            "to": "test@gmail.com",
            "from_email": "test@gmail.com",
            "subject": "thisi s a test",
            "text": "text"
        }
        mock = Mock()
        mock.send.side_effect = EmailServiceResponseException(400, "Fake")
        mock_loader.return_value = mock
        mock_retry.side_effect = Retry

        self.assertRaises(Retry, tasks.send_mail.delay, form)
