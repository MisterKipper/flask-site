import unittest

from app import create_app, db
from app.exceptions import ValidationError
from app.models import Comment, Post, Role, User
from app.auth.forms import RegistrationForm


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

    @staticmethod
    def add_user(username="brian",
                 email="brian@example.com",
                 password="abc",
                 role="admin",
                 active=True):
        r = Role.query.filter_by(name=role).first()
        u = User(username=username, email=email, password=password, role=r, active=active)
        db.session.add(u)
        db.session.commit()
        return u

    @staticmethod
    def add_post(author, body="original-post"):
        p = Post(body=body, author=author)
        db.session.add(p)
        db.session.commit()
        return p

    def login(self, username="brian", password="abc"):
        response = self.client.post("/auth/login",
                                    data={
                                        "username": username,
                                        "password": password
                                    },
                                    follow_redirects=True)
        return response

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Welcome to Kyle's junk!" in response.get_data(as_text=True))

    def test_register_and_login(self):
        # Test registration
        response = self.client.post("/auth/register",
                                    data={
                                        "email": "brian@example.com",
                                        "username": "brian",
                                        "password": "abc",
                                        "password2": "abc"
                                    })
        self.assertEqual(response.status_code, 302)

        # Test login
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Inactive account" in response.get_data(as_text=True))

        # Test account activation
        user = User.query.filter_by(username="brian").first()
        token = user.generate_activation_token()
        response = self.client.get(f"/auth/activate/{token}", follow_redirects=True)
        user.activate(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Account activated." in response.get_data(as_text=True))

        # Test logout
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("You have been logged out." in response.get_data(as_text=True))

    def test_registration_form(self):
        # Add user
        form = RegistrationForm(username="brian",
                                email="brian@example.com",
                                password="abc",
                                password2="abc")
        self.assertTrue(form.validate())

        self.add_user(form.username.data, form.email.data, form.password.data)

        # Add user with same email
        form = RegistrationForm(username="not_brian",
                                email="brian@example.com",
                                password="abc",
                                password2="abc")
        self.assertFalse(form.validate())
        self.assertEqual(form.errors["email"][0], "Email address already in use.")

        # Add user with same username
        form = RegistrationForm(username="brian",
                                email="not_brian@example.com",
                                password="abc",
                                password2="abc")
        self.assertFalse(form.validate())
        self.assertEqual(form.errors["username"][0], "Username already in use.")

        # Test passwords not equal
        form = RegistrationForm(username="not_brian",
                                email="not_brian@example.com",
                                password="abc",
                                password2="xyz")
        self.assertFalse(form.validate())
        self.assertEqual(form.errors["password2"][0], "Field must be equal to password.")

    def test_get_post(self):
        u = self.add_user()
        p = self.add_post(u)

        self.login()
        response = self.client.get(f"/post/{p.id}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("original-post" in response.get_data(True))

        response = self.client.get(f"/post/{p.id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_make_post(self):
        # TODO: Test lack of permissions, unactivated account, etc.
        u = self.add_user()

        # Test making post
        self.login()
        response = self.client.post("/",
                                    data={"body": "# Test post\n- Testing\n- testing"},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        p = Post.query.order_by(Post.timestamp.desc()).first()
        self.assertEqual(p.author, u)
        self.assertEqual(p.body_html,
                         "<h1>Test post</h1>\n<ul>\n<li>Testing</li>\n<li>testing</li>\n</ul>")

    def test_edit_post(self):
        u = self.add_user()
        p = self.add_post(u)
        self.login()
        # Test GET
        response = self.client.get(f"/post/edit/{p.id}")
        self.assertTrue(p.body in response.get_data(True))

        # Test successful edit
        response = self.client.post(f"/post/edit/{p.id}",
                                    data={"body": "update-post!"},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(p.body, "update-post!")
        self.client.get("/auth/logout")

        # Test non-author, non-admin
        p = self.add_post(u)
        u_bad = self.add_user("bob", "bob@example.com", "xyz", "user")
        self.login("bob", "xyz")
        response = self.client.post(f"/post/edit/{p.id}",
                                    data={"body": "update-post!"},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(p.body, "original-post")

    def test_comment(self):
        u = self.add_user()
        p = self.add_post(u)

        self.login()
        response = self.client.post(f"/post/{p.id}", data={"body": "test comment asdfghjkl"})
        c = Comment.query.filter_by(post=p).first()
        self.assertEqual(c.post, p)
        self.assertTrue("asdfghjkl" in c.body)

    def test_edit_comment(self):
        u = self.add_user()
        p = self.add_post(u)
        c = Comment(body="Test comment", post=p, author=u)
        db.session.add(c)
        db.session.commit()
        self.login()

        # Test GET
        response = self.client.get(f"/comment/edit/{c.id}")
        self.assertTrue(c.body in response.get_data(True))

        # Test successful edit
        response = self.client.post(f"/comment/edit/{c.id}",
                                    data={"body": "update-comment!"},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(c.body, "update-comment!")
        self.client.get("/auth/logout")

        # Test non-author, non-admin
        c = Comment(body="Test comment", post=p, author=u)
        db.session.add(c)
        db.session.commit()
        u_bad = self.add_user("bob", "bob@example.com", "xyz", "user")
        self.login("bob", "xyz")
        response = self.client.post(f"/comment/edit/{c.id}",
                                    data={"body": "update-comment!"},
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(c.body, "Test comment")

    def test_reply_to_comment(self):
        u = self.add_user()
        p = self.add_post(u)
        c = Comment(body="first-comment", post=p, author=u)
        db.session.add(c)
        db.session.commit()

        u_user = self.add_user("bob", "bob@example.com", "xyz", "user")
        self.login("bob", "xyz")

        # Test GET
        response = self.client.get(f"/comment/reply/{c.id}",)
        self.assertTrue(c.body in response.get_data(True))

        # Test reply
        response = self.client.post(f"/comment/reply/{c.id}",
                                    data={"body": "reply-to-first-comment"})
        c2 = Comment.query.order_by(Comment.timestamp.desc()).first()
        self.assertEqual(c2.parent, c)
        self.assertEqual(c2.body, "reply-to-first-comment")
        self.assertEqual(c2.post, p)

    def test_user(self):
        u = self.add_user()

        self.login()
        response = self.client.get("/user/brian")
        self.assertTrue("<title>brian - Kyle's junk</title>" in response.get_data(True))
