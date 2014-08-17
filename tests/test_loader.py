import unittest

import loader
from services import mandrill, mailgun


class TestLoader(unittest.TestCase):
    def test_contents(self):
        loader.get_random_email_service()
        services = loader.get_email_services()
        self.assertTrue(mandrill.MandrillService in services)
        self.assertTrue(mailgun.MailgunService in services)
