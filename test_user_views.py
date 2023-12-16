import unittest
from models import db, User, Message, Follows
from app import app
from flask import session

# Set up the test environment
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler_test'
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

class ViewFunctionTests(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        db.drop_all()
        db.create_all()

        # Create a test client
        self.client = app.test_client()

        # Create test users
        self.user1 = User.create(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.create(username='user2', email='user2@example.com', password='password123')

        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        db.session.rollback()
        db.drop_all()

    def test_logged_in_can_see_follower_page(self):
        """When logged in, can you see the follower page for any user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = c.get(f'/users/{self.user2.id}/followers')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Follower", response.data)

    # Add more tests for other questions

    def test_logged_out_disallowed_from_follower_page(self):
        """When logged out, are you disallowed from visiting a user’s follower page?"""
        response = self.client.get(f'/users/{self.user2.id}/followers')
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_logged_in_can_add_message(self):
        """When logged in, can you add a message as yourself?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = c.post('/messages/new', data={'text': 'Test message'}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Test message", response.data)
            self.assertTrue(Message.query.filter_by(text='Test message', user_id=self.user1.id).first())

    # Add more tests for other questions

    def test_logged_out_prohibited_from_adding_messages(self):
        """When logged out, are you prohibited from adding messages?"""
        response = self.client.post('/messages/new', data={'text': 'Test message'})
        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_logged_in_prohibited_from_adding_message_as_another_user(self):
        """When logged in, are you prohibited from adding a message as another user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = c.post(f'/users/{self.user2.id}/messages/new', data={'text': 'Test message'})
            self.assertEqual(response.status_code, 403)  # Forbidden

    # Add more tests for other questions

if __name__ == '__main__':
    unittest.main()
