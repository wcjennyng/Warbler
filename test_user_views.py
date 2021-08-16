"""User view tests"""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class MessageViewTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        """Create test client, add sample data"""

        db.drop_all()
        db.create_all()

        self.testuser = User.signup(username='testuser', email='testuser@gmail.com', password='password', image_url=None)
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        self.u1 = User.signup('user1','user1@gmail.com', 'password', None)
        self.u1_id = 1122
        self.u1.id = self.u1_id

        self.u2 = User.signup('user2','user2@gmail.com', 'password', None)
        self.u2_id = 2211
        self.u2.id = self.u2_id

        self.u3 = User.signup('user3', 'user3@gmail.com', 'password', None)
        self.u4 = User.signup('user4', 'user4@gmail.com', 'password', None)

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()

    def test_users_index(self):
        with self.client as c:
            res = c.get('/users')

            self.assertIn('@testuser', str(res.data))
            self.assertIn('@user1', str(res.data))
            self.assertIn('@user2', str(res.data))
            self.assertIn('@user3', str(res.data))
            self.assertIn('@user4', str(res.data))

    def test_users_search(self):
        with self.client as c:
            res = c.get('/users?q=test')

            self.assertIn('@testuser', str(res.data))
            self.assertNotIn('@user1', str(res.data))

    def test_user_show(self):
        with self.client as c: 
            res = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', str(res.data))

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2])
        db.session.commit()

    def test_show_following(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f"/users/{self.testuser_id}/following")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@user1", str(res.data))
            self.assertNotIn("@user3", str(res.data))
            self.assertNotIn("@user4", str(res.data))

    def test_show_followers(self):

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f"/users/{self.testuser_id}/followers")
            self.assertEqual(res.status_code, 200)
            self.assertIn("@user1", str(res.data))
            self.assertNotIn("@user2", str(res.data))
            self.assertNotIn("@user3", str(res.data))
            self.assertNotIn("@user4", str(res.data)) 

    def test_unauthorized_following_page_access(self):

        self.setup_followers()
        with self.client as c:

            res = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn("@user1", str(res.data))
            self.assertIn("Access unauthorized", str(res.data))

    def test_unauthorized_followers_page_access(self):

        self.setup_followers()
        with self.client as c:

            res = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn("@user1", str(res.data))
            self.assertIn("Access unauthorized", str(res.data))



    



