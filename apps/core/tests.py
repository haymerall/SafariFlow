# pyrefly: ignore [missing-import]
from django.test import TestCase

class CoreAppTest(TestCase):
    def test_app_loads(self):
        self.assertTrue(True)
