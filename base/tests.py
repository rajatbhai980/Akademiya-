import importlib
import os

from django.test import SimpleTestCase


class SettingsDefaultsTests(SimpleTestCase):
    def test_missing_email_port_defaults_to_587(self):
        settings_module = importlib.import_module('Akademiya.settings')
        original_email_port = os.environ.get('EMAIL_PORT')
        os.environ.pop('EMAIL_PORT', None)

        try:
            reloaded_settings = importlib.reload(settings_module)
            self.assertEqual(reloaded_settings.EMAIL_PORT, 587)
        finally:
            if original_email_port is None:
                os.environ.pop('EMAIL_PORT', None)
            else:
                os.environ['EMAIL_PORT'] = original_email_port
            importlib.reload(settings_module)
