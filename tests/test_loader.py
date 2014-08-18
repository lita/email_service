import unittest
from mock import patch

import loader
from services import mandrill, mailgun


class TestLoader(unittest.TestCase):
    def test_contents(self):
        loader.get_random_email_service()
        services = loader.email_services
        self.assertTrue(mandrill.MandrillService in services)
        self.assertTrue(mailgun.MailgunService in services)

        # If we clear the contents, should reload the services
        loader.email_services = []
        loader.get_random_email_service()
        self.assertTrue(mandrill.MandrillService in services)
        self.assertTrue(mailgun.MailgunService in services)

    @patch("loader.path.files")
    def empty_plugins(self, mock):
        mock.return_value = []
        result = loader.get_random_email_service()
        self.assertEquals(result, None)

    @patch("loader.random.choice")
    def check_get_instance_of_class(self, mock):
        mock.return_value = mandrill.MandrillService
        result = self.get_random_email_service()
        self.assertTrue(isinstance(result, mandrill.MandrillService))
