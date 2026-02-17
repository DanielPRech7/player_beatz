from django.test import TestCase
from django.db import models
from uuid import UUID
from beats.core.models import AbstractBaseModel

class AbstractBaseModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        class TestModel(AbstractBaseModel):
            nome = models.CharField(max_length=100)

            class Meta:
                app_label = 'core'
                managed = False

        cls.TestModel = TestModel
        cls.obj = cls.TestModel(nome="Teste")
        cls.obj.uuid = cls.obj.uuid or UUID("00000000-0000-0000-0000-000000000000")
        import datetime
        now = datetime.datetime.now()
        cls.obj.created_at = now
        cls.obj.updated_at = now

    def test_uuid_field(self):
        self.assertIsInstance(self.obj.uuid, UUID)

    def test_created_at_field(self):
        self.assertIsNotNone(self.obj.created_at)

    def test_updated_at_field(self):
        self.assertIsNotNone(self.obj.updated_at)
