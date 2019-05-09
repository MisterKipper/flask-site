import unittest

from app import create_app, db
from app.models import Role, User


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Welcome to Kyle's junk!" in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post("/auth/register",
                                    data={
                                        "email": "brian@example.com",
                                        "username": "brian",
                                        "password": "abc",
                                        "password2": "abc"
                                    })
        self.assertEqual(response.status_code, 302)

        response = self.client.post("/auth/login",
                                    data={
                                        "username": "brian",
                                        "password": "abc"
                                    },
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Inactive account" in response.get_data(as_text=True))

        user = User.query.filter_by(username="brian").first()
        token = user.generate_activation_token()
        response = self.client.get(f"/auth/activate/{token}", follow_redirects=True)
        user.activate(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Account activated." in response.get_data(as_text=True))

        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("You have been logged out." in response.get_data(as_text=True))
