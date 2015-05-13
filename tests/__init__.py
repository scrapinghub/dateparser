# -*- coding: utf-8 -*-
from unittest import TestCase


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.__patches = []

        self.error = NotImplemented

    def add_patch(self, patch):
        patch.start()
        self.__patches.append(patch)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        for patch in reversed(self.__patches):
            patch.stop()

    def then_error_was_raised(self, error_cls, error_message):
        self.assertIsInstance(self.error, error_cls)
        self.assertEqual(error_message, str(self.error))
