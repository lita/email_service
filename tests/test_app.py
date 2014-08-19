import unittest
from mock import patch

import app


class TestFlaskApp(unittest.TestCase):

    def test_check_form_values(self):
        form = {
            "to": "test@gmail.com"
        }
        self.assertRaises(app.InvalidFormError, app.check_form_values, form)

        form = {
            "to": "test@gmail.com",
            "from_email": "test@gmail.com",
            "subject": "thisi s a test",
            "text": "text"
        }
        self.assertEqual(app.check_form_values(form), None)

    @patch("app.request")
    @patch("app.check_form_values")
    @patch("app.tasks")
    def test_send_email(self, mock_tasks, mock_form_values, mock_request):
        class FakeTask():
            def get(self, timeout=0):
                return "Fake Service"
        form = {
            "to": "test@gmail.com",
            "from_email": "test@gmail.com",
            "subject": "thisi s a test",
            "text": "text"
        }
        mock_form_values.return_value = True
        mock_request.form.to_dict.return_value = form
        mock_tasks.send_mail.delay.return_value = FakeTask()
        app.send_email()
        self.assertTrue(mock_tasks.send_mail.delay.called)
        self.assertTrue(mock_form_values.called)
