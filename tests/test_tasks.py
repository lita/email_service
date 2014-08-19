import unittest
from mock import patch, Mock
from celery.exceptions import Retry

import tasks
from services import EmailServiceResponseException


class TestTasks(unittest.TestCase):
    def setUp(self):
        tasks.app.conf.CELERY_ALWAYS_EAGER = True
        tasks.app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    def tearDown(self):
        tasks.app.conf.CELERY_ALWAYS_EAGER = False
        tasks.app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

    def test_send_email_validation(self):
        form = {
            "to": "test@gmail.com",
            "from_email": "no email",
        }
        self.assertEquals(tasks.send_mail(form),
                          "Email wasn't formatted properly.")

        form = {
            "to": "test.com",
            "from_email": "lita.cho@what.com",
        }
        self.assertEquals(tasks.send_mail(form),
                          "Email wasn't formatted properly.")

    def test_validate_emails(self):
        good_emails = "what@example,who@example.edu,fake@hey.com"
        emails, errors = tasks.validate_emails(good_emails)
        expected = ["what@example", "who@example.edu", "fake@hey.com"]
        self.assertItemsEqual(emails, expected)
        self.assertEquals(errors, [])

        good_and_bad_emails = "what@example,   fake, fake@hey.com"
        emails, errors = tasks.validate_emails(good_and_bad_emails)
        expected = ["what@example", "fake@hey.com"]
        expected_error = ["fake"]
        self.assertItemsEqual(emails, expected)
        self.assertEquals(errors, expected_error)

        good_email = "hello@hey.com"
        emails, errors = tasks.validate_emails(good_email)
        self.assertItemsEqual(emails, ["hello@hey.com"])
        self.assertEquals(errors, [])

    @patch("tasks.send_mail.retry")
    @patch("tasks.loader.get_random_email_service")
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

    @patch("tasks.send_mail.retry")
    @patch("tasks.loader.get_random_email_service")
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
