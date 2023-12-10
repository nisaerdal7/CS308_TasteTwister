import unittest
from unittest.mock import Mock, patch, MagicMock

from flask_bcrypt import Bcrypt
from app_jsonified import app, add_or_update_song, FriendRequest, friendships

bcrypt = Bcrypt(app)
class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Create a mock database and user for testing
        self.app = app.test_client()
        self.mock_user_instance = Mock()
        self.mock_user_instance.username = 'testuser'
        self.mock_user_instance.token = 'valid_token'
        self.mock_user_instance.password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
        self.app_context = app.app_context()
        self.app_context.push()
    def tearDown(self):
    # Pop the Flask application context
        self.app_context.pop()

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

    @patch('app_jsonified.Client')
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_add_or_update_song(self, mock_db_session, mock_user_query, mock_song_query, mock_client):
        # Mock the necessary objects and methods
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        mock_song_instance = MagicMock()
        mock_song_query.filter_by.return_value.first.return_value = mock_song_instance

        mock_user_instance = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_user_instance.permission = True  # Set the user's permission as needed

        mock_track = MagicMock()
        mock_track.name = 'Mock Track'
        mock_artist = MagicMock(name='Mock Artist')
        mock_artist.name = 'Mock Artist Name'  # Set the artist name
        mock_track.artists = [mock_artist]
        mock_track.album.name = 'Mock Album'

        mock_search_result = MagicMock()
        mock_search_result.get_tracks.return_value = [mock_track]
        mock_client.return_value.search.return_value = mock_search_result

        # Call the function
        add_or_update_song(mock_track.name, mock_artist.name, mock_track.album.name, '5', 'username')

        # Assertions
        mock_song_query.filter_by.assert_called_once_with(
            track_name='Mock Track', performer='Mock Artist Name', album='Mock Album', username='username'
        )
        mock_song_query.filter_by.return_value.first.assert_called_once()

    @patch('app_jsonified.User.query')  # Replace 'app' with the actual module name
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_logout_route(self, mock_session, mock_user_query):
        # Set the behavior of the query method to simulate a valid user
        mock_user_query.filter_by.return_value.first.return_value = self.mock_user_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a logout request
        headers = {'Authorization': 'valid_token'}
        response = client.post('/logout', headers=headers)

        # Assert that the logout is successful
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Logged out successfully')

        # Check if the user query was called
        mock_user_query.filter_by.assert_called_once_with(token='valid_token')
        mock_user_query.filter_by.return_value.first.assert_called_once()
        # Check if commit method was called on the session
        

    @patch('app_jsonified.User.query')  # Replace 'your_application_module' with the actual module name
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    @patch('app_jsonified.friendships', new_callable=MagicMock)
    @patch('app_jsonified.FriendRequest.query')
    def test_send_invite_route(self, mock_friend_request_query, mock_session, mock_friendships, mock_user_query):
        # Set the behavior of the query method to simulate an existing user
        mock_user_query.filter_by.return_value.first.return_value = self.mock_user_instance

        # Mock the necessary objects and methods
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        # Simulate an existing friendship
        mock_friendship_instance = MagicMock()
        mock_friendship_instance.c.user1 = 'testuser'
        mock_friendship_instance.c.user2 = 'receiver_username'
        mock_session.query.return_value.filter.return_value.first.return_value = mock_friendship_instance

        # Send an invite request
        data = {'receiver': 'receiver_username'}
        headers = {'Authorization': 'mock_token'}
        response = self.app.post('/send_invite', json=data, headers=headers)

        # Assert that the response is as expected for an existing friendship
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You are already friends')






if __name__ == '__main__':
    unittest.main()