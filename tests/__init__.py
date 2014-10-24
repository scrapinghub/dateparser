# -*- coding: utf-8 -*-
from unittest import TestCase


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.__patches = []

    def add_patch(self, patch):
        patch.start()
        self.__patches.append(patch)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        for patch in reversed(self.__patches):
            patch.stop()
