import unittest

from flask import current_app

from app.models import User, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.u = User(password="boss")

    def test_password_setter(self):
        self.assertTrue(self.u.password_hash is not None)

    def test_password_verification(self):
        self.assertTrue(self.u.verify_password("boss"))
        self.assertFalse(self.u.verify_password("chief"))

    def test_password_salts_are_random(self):
        u2 = User(password="boss")
        self.assertFalse(self.u.password_hash == u2.password_hash)

    def test_admin_role(self):
        u = User(email=current_app.config["ADMIN_ADDRESS"], password="boss")
        for perm in ["FOLLOW", "COMMENT", "WRITE", "MODERATE", "ADMIN"]:
            self.assertTrue(u.can(getattr(Permission, perm)))

    def test_user_role(self):
        u = User(email="example@example.com", password="user")
        for perm in ["FOLLOW", "COMMENT", "WRITE"]:
            self.assertTrue(u.can(getattr(Permission, perm)))
        for perm in ["MODERATE", "ADMIN"]:
            self.assertFalse(u.can(getattr(Permission, perm)))

    def test_anonymous_user(self):
        u = AnonymousUser()
        for perm in ["FOLLOW", "COMMENT", "WRITE", "MODERATE", "ADMIN"]:
            self.assertFalse(u.can(getattr(Permission, perm)))
