import json
import unittest
from base64 import b64encode

from flask import url_for

from app import create_app, db
from app.models import Comment, Post, Role, User


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.add_user()
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

    def add_user(self, username="thanos", password="inevitable", role="user", active=True):
        r = Role.query.filter_by(name=role).first()
        u = User(username=username, password=password, active=active, role=r)
        db.session.add(u)
        db.session.commit()
        return u

    def test_404(self):
        response = self.client.get("/this/url/does/not/exist",
                                   headers=self.get_api_headers("username", "password"))
        self.assertEqual(response.status_code, 404)
        json_response = response.get_json()
        self.assertEqual(json_response["error"], "not found")

    def test_no_auth(self):
        response = self.client.get("/api/v1/posts",
                                   content_type="application/json",
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        response = self.client.get("/api/v1/posts/",
                                   headers=self.get_api_headers("thanos", "iron man"),
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_token_auth(self):
        # Test bad token
        response = self.client.get("/api/v1/posts/",
                                   headers=self.get_api_headers("bad-token", ""),
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 401)

        # Get a token
        response = self.client.post("/api/v1/tokens/",
                                    headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertIsNotNone(json_response.get("token"))
        token = json_response["token"]

        # Test token
        response = self.client.get("/api/v1/posts/",
                                   headers=self.get_api_headers(token, ""),
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_anonymous(self):
        response = self.client.get("/api/v1/posts/",
                                   headers=self.get_api_headers("", ""),
                                   follow_redirects=True)
        self.assertEqual(response.status_code, 401)

    def test_inactive_account(self):
        self.add_user("thor", "strongest avenger", "user", False)

        response = self.client.post("/api/v1/posts/",
                                    headers=self.get_api_headers("thor", "strongest avenger"),
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 403)

    def test_posts(self):
        u = self.add_user("hulk", "smash", "admin")

        # write an empty post
        response = self.client.post("/api/v1/posts/",
                                    headers=self.get_api_headers("hulk", "smash"),
                                    data=json.dumps({"body": ""}))
        self.assertEqual(response.status_code, 400)

        # write a post
        body = "# Test post\n- One\n- Two"
        body_html = "<h1>Test post</h1>\n<ul>\n<li>One</li>\n<li>Two</li>\n</ul>"
        response = self.client.post("/api/v1/posts/",
                                    headers=self.get_api_headers("hulk", "smash"),
                                    data=json.dumps({"body": body}))
        self.assertEqual(response.status_code, 201)
        url = response.headers.get("Location")
        self.assertIsNotNone(url)

        response = self.client.get(url, headers=self.get_api_headers("hulk", "smash"))
        self.assertEqual(response.status_code, 200)
        json_post = response.get_json()
        self.assertEqual("http://localhost" + json_post["url"], url)
        self.assertEqual(json_post["body"], body)
        self.assertEqual(json_post["body_html"], body_html)

        # Get the post from the user
        response = self.client.get(f"api/v1/users/{u.id}/posts/",
                                   headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertIsNotNone(json_response.get("posts"))
        self.assertEqual(json_response.get("count", 0), 1)
        self.assertEqual(json_response["posts"][0], json_post)

        # Edit post
        response = self.client.put(url,
                                   headers=self.get_api_headers("hulk", "smash"),
                                   data=json.dumps({"body": "update"}))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual("http://localhost" + json_response["url"], url)
        self.assertEqual(json_response["body"], "update")
        self.assertEqual(json_response["body_html"], "<p>update</p>")

    def test_users(self):
        u1 = self.add_user("thor", "strongest avenger")
        u2 = self.add_user("hulk", "smash", "admin")

        bad_id = User.query.order_by(User.id.desc()).first().id + 1
        response = self.client.get(f"/api/v1/users/{bad_id}",
                                   headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(f"/api/v1/users/{u1.id}",
                                   headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response["username"], "thor")

        response = self.client.get(f"/api/v1/users/{u2.id}",
                                   headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response["username"], "hulk")

    def test_comments(self):
        # Add a post
        u_admin = self.add_user("hulk", "smash", "admin")
        post = Post(body="Test post", author=u_admin)
        db.session.add(post)
        db.session.commit()

        # Add a comment
        u_user = self.add_user("thor", "strongest avenger")
        response = self.client.post(f"/api/v1/posts/{post.id}/comments/",
                                    headers=self.get_api_headers("thor", "strongest avenger"),
                                    data=json.dumps({"body": "[Test comment](http://example.com)"}))
        self.assertEqual(response.status_code, 201)
        json_response = response.get_json()
        url = response.headers.get("Location")
        self.assertIsNotNone(url)
        self.assertEqual(json_response["body"], "[Test comment](http://example.com)")
        self.assertEqual(json_response["body_html"],
                         '<p><a href="http://example.com" rel="nofollow">Test comment</a></p>')

        response = self.client.get(url, headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual("http://localhost" + json_response["url"], url)
        self.assertEqual(json_response["body"], "[Test comment](http://example.com)")

        comment = Comment(body="Yes", author=u_admin, post=post)
        db.session.add(comment)
        db.session.commit()

        response = self.client.get(f"/api/v1/posts/{post.id}/comments/",
                                   headers=self.get_api_headers("thanos", "inevitable"))
        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertIsNotNone(json_response.get("comments"))
        self.assertEqual(json_response.get("count", 0), 2)
