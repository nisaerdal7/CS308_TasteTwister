import unittest
from unittest.mock import Mock, patch, MagicMock

from flask_bcrypt import Bcrypt
from app_jsonified import app

bcrypt = Bcrypt(app)
class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Create a mock database and user for testing
        self.app = app.test_client()
        self.mock_user_instance = Mock()
        self.mock_user_instance.username = 'testuser'
        self.mock_user_instance.password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
    @patch('app_jsonified.User.query')  # Replace 'your_application_module' with the actual module name
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_register_route(self, mock_session, mock_user_query):
        # Set the behavior of the query method to simulate a non-existing user
        mock_user_query.filter_by.return_value.first.return_value = None  # Simulate non-existing user

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a registration request
        data = {'username': 'newuser', 'password': 'testpassword', 'permission': True}
        response = client.post('/register', json=data)

        # Assert that the registration is successful
        self.assertEqual(response.status_code, 201)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Registration successful!')

        # Check if the user query was called
        mock_user_query.filter_by.assert_called_once_with(username='newuser')
        mock_user_query.filter_by.return_value.first.assert_called_once()
        # Check if add and commit methods were called on the session
        self.assertTrue(mock_session.add.called)
        self.assertTrue(mock_session.commit.called)
    @patch('app_jsonified.User')
    def test_successful_login(self, mock_user):
        # Set the behavior of the query method for the mock user
        mock_user.query.filter_by.return_value.first.return_value = self.mock_user_instance
        # Set the behavior of the check_password_hash method for bcrypt
        bcrypt.check_password_hash = True

        # Prepare login data
        login_data = {'username': 'testuser', 'password': 'testpassword'}

        # Make a POST request to the login route
        response = self.app.post('/login', json=login_data)

        # Assert that the login was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        self.assertEqual(response.json['message'], 'Login successful!')


if __name__ == '__main__':
    unittest.main()
