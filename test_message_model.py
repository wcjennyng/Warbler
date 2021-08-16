"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User.signup('user', 'user@gmail.com', 'password', None)
        uid = 1234
        u.id = uid

        db.session.commit()

        u = User.query.get(uid)

        self.u = u
        self.uid = uid

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text='message',
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, 'message')


    