import json
import unittest
from base64 import b64encode

from flask import url_for

from app import create_app, db
from app.models import Role, User


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            "Authorization":
                "Basic " + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
            "Accept":
                "application/json",
            "Content-Type":
                "application/json"
        }

    def test_no_auth(self):
        response = self.client.get(url_for("api.get_posts"), content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_posts(self):
        r = Role.query.filter_by(name="User").first()
        u = User(username="brian", password="life", active=True, role=r)
        db.session.add(u)
        db.session.commit()

        body = "# Test post\n- One\n- Two"
        body_html = "<h1>Test post</h1><ul><li>One</li><li>Two</li></ul>"
        response = self.client.post("/api/v1/posts/",
                                    headers=self.get_api_headers("brian", "life"),
                                    data=json.dumps({"body": body}))
        self.assertEqual(response.status_code, 201)
        url = response.headers.get("Location")
        self.assertIsNotNone(url)

        response = self.client.get(url, headers=self.get_api_headers("brian", "life"))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual("http://localhost" + json_response["url"], url)
        self.assertEqual(json_response["body"], body)
        self.assertEqual(json_response["body_html"], body_html)
