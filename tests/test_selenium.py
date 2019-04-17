import unittest

import app.utils as utils
from app import create_app, db
from app.models import Role
from selenium import webdriver


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        try:
            cls.client = webdriver.Chrome(chrom_options=options)
        except:
            pass

        if cls.client:
            cls.app = create_app("testing")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")

            db.create_all()
            Role.insert_roles()
            utils.insert_admin()
            utils.insert_fake_users(10)
            utils.insert_fake_posts(10)

            cls.server_thread = threading.Thread(target=cls.app.run,
                                                 kwargs={
                                                     "debug": "false",
                                                     "use_reloader": False,
                                                     "use_debugger": False
                                                 })
            cls.server_thread.start()

        @classmethod
        def tearDownClass(cls):
            if cls.client:
                cls.client.get("http://localhost:5000/shutdown")
                cls.client.quit()
                cls.server_thread.join()

                db.drop_all()
                db.session.remove()

                cls.app_context.pop()

        def setUp(self):
            if not self.client:
                self.skipTest("Web browser not available")

        def tearDown(self):
            pass
