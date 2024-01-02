import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from io import BytesIO
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
        add_or_update_song('Track Name', 'Performer', 'Album', '5', 'username')

        # Assertions
        mock_song_query.filter_by.assert_called_once_with(
            track_name='Track Name', performer='Performer', album='Album', username='username'
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

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.Song.query')
    def test_user_stats_route(self, mock_user_query, mock_song_query):
        # Set up the behavior of the query methods to simulate existing user and songs
        mock_user_instance = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_song_instance = MagicMock()
        mock_song_query.filter_by.return_value = mock_song_instance

            # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to user_stats route
        response = client.get('/stats/all-time/testuser')

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('top_songs', data)
        self.assertIn('top_albums', data)
        self.assertIn('top_performers', data)

        # Check if the user and song queries were called
        mock_user_query.filter_by.assert_called_with(username='testuser')
        mock_song_query.filter_by.assert_called_with(username='testuser')
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_block_friend_route(self, mock_session, mock_user_query):
       
       mock_user_query.filter_by.return_value.first.return_value = None  # Simulate non-existing user
       # Set up a test client
       app.config['TESTING'] = True
       client = app.test_client()

       # Send a block friend request
       data = {'blocker': 'testuser', 'blocked': 'blocked_user'}
       response = client.post('/block_friend', json=data)

       # Assert that the blocking is successful
       self.assertEqual(response.status_code, 200)
       data = response.json
       self.assertIn('message', data)
       self.assertEqual(data['message'], 'blocked_user blocked')

       # Check if the user query was called
       #mock_user_query.get.assert_called_with(username='testuser')
       mock_user_query.get.assert_called_with('blocked_user')

       # Check if add and commit methods were called on the session
       self.assertTrue(mock_session.commit.called)


    @patch('app_jsonified.User.query')  # Replace 'app_jsonified' with the actual module name
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_view_blocked_friends_route(self, mock_session, mock_user_query):
        # Set the behavior of the query method to simulate an existing user
        mock_user_instance = MagicMock()
        mock_user_instance.blocked.all.return_value = [MagicMock(username='blocked_user')]

        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to view blocked friends
        headers = {'Authorization': 'valid_token'}
        response = client.get('/blocked_friends', headers=headers)

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'blocked_user')

        # Check if the user query was called
        mock_user_query.filter_by.assert_called_with(token='valid_token')  # Change assert_called_once_with to assert_called_with
        # Check if commit method was called on the session
        #self.assertTrue(mock_session.commit.called)
        #mock_session.commit.assert_called_once()
    
    @patch('app_jsonified.FriendRequest.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_view_incoming_invites_route(self, mock_session, mock_user_query, mock_friend_request_query):
        # Test the view_incoming_invites route
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_friend_request_instance = MagicMock()
        mock_friend_request_instance.sender = 'friend_sender'
        mock_friend_request_instance.sent_at = datetime.utcnow()
        mock_friend_request_instance.status = 'pending'
        mock_friend_request_query.filter_by.return_value.filter.return_value.all.return_value = [mock_friend_request_instance]

        # Send a request to view incoming invites
        headers = {'Authorization': 'valid_token'}
        response = self.app.get('/incoming_invites', headers=headers)

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
    
    @patch('app_jsonified.User.query')
    def test_view_outgoing_invites(self, mock_user_query):
        # Set up the behavior of the query method to simulate an existing user
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to view outgoing invites
        headers = {'Authorization': 'valid_token'}
        response = client.get('/outgoing_invites', headers=headers)

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.FriendRequest.query')
    def test_respond_invite(self, mock_friend_request_query, mock_user_query):
        # Set up the behavior of the query method to simulate an existing user
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Set up the behavior of the query method to simulate an existing invite
        mock_invite_instance = MagicMock()
        mock_invite_instance.id = 1
        mock_invite_instance.receiver = 'testuser'
        mock_invite_instance.status = 'pending'
        mock_friend_request_query.filter_by.return_value.first.return_value = mock_invite_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a respond invite request
        data = {'invite_id': 1, 'response': 'accept'}
        response = client.post('/respond_invite', json=data, headers={'Authorization': 'valid_token'})

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('message', data)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    def test_view_friends(self, mock_user_query):
        # Set up the behavior of the query method to simulate an existing user
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.friends = [MagicMock(username='friend1'), MagicMock(username='friend2')]
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to view friends
        response = client.get('/friends/testuser')

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_remove_friend_route(self, mock_session, mock_user_query):
        # Set up the behavior of the query method to simulate an existing user
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.friends = [MagicMock(username='friend_to_remove')]
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a remove friend request
        data = {'friend_username': 'friend_to_remove'}
        response = client.post('/remove_friend', json=data, headers={'Authorization': 'valid_token'})

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 404)
        data = response.json
        self.assertIn('message', data)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_recommend_playlist_all_users_route(self, mock_session, mock_song_query, mock_user_query):
        # Set up the behavior of the query methods to simulate existing user and songs
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_song_instance = MagicMock()
        mock_song_query.filter.return_value = mock_song_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to recommend playlist for all users
        response = client.get('/recommend_playlist_all_users', headers={'Authorization': 'valid_token'})

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_recommend_playlist_friends_duo_route(self, mock_session, mock_song_query, mock_user_query):
        # Set up the behavior of the query methods to simulate existing user, friend, and songs
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_friend_instance = MagicMock()
        mock_friend_instance.username = 'friend_user'
        mock_user_instance.friends = [mock_friend_instance]

        mock_song_instance_user = MagicMock()
        mock_song_instance_user.username = 'testuser'
        mock_song_instance_user.rating = 4
        mock_song_query.filter.return_value = mock_song_instance_user

        mock_song_instance_friend = MagicMock()
        mock_song_instance_friend.username = 'friend_user'
        mock_song_instance_friend.rating = 4
        mock_song_query.filter.return_value = mock_song_instance_friend

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to recommend playlist for friends duo
        response = client.get('/recommend_playlist_friends_duo', headers={'Authorization': 'valid_token'}, query_string={'friend_username': 'friend_user'})

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 404)
        data = response.json
        # Update the assertion for the data type
        self.assertIsInstance(data, dict)
        # Add an additional assertion for the error message
        self.assertEqual(data['error'], 'Friend not found or users are not friends')

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_recommend_playlist_from_all_friends_route(self, mock_session, mock_song_query, mock_user_query):
        # Set up the behavior of the query methods to simulate existing user and friends
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.friends = [MagicMock(username='friend1'), MagicMock(username='friend2')]
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_song_instance = MagicMock()
        mock_song_query.filter.return_value = mock_song_instance

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send a request to recommend playlist from all friends
        response = client.get('/recommend_playlist_from_all_friends', headers={'Authorization': 'valid_token'})

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIsInstance(data, list)
        # Add more assertions based on the expected behavior of the route

    @patch('app_jsonified.allowed_file')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_upload_songs(self, mock_session, mock_user_query, mock_allowed_file):
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_allowed_file.return_value = True

        data = {
            'file': (BytesIO(b'sample,data'), 'test.csv')
        }
        headers = {'Authorization': 'valid_token'}
        response = self.app.post('/upload_songs', data=data, content_type='multipart/form-data', headers=headers)

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(response.json['message'], 'Songs uploaded successfully!')
    
    '''
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    def test_get_unrated_songs(self, mock_user_query, mock_song_query):
        # Mock User instance
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        # Mock Song instance
        mock_song_instance = MagicMock()
        mock_song_instance.id = 1
        mock_song_instance.title = "Test Song"
        mock_song_instance.artist = "Test Artist"
        
        # Ensure the all() method returns a list of these mocked Song objects
        mock_song_query.filter.return_value.all.return_value = [mock_song_instance]

        # Make the API call
        response = self.app.get('/songs/unrated', query_string={'username': 'testuser'})

        # Test assertions
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    '''

    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_update_song_rating(self, mock_session, mock_user_query, mock_song_query):
        mock_song_instance = MagicMock()
        mock_song_instance.user.username = 'testuser'
        mock_song_query.get.return_value = mock_song_instance

        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        data = {'new_rating': 5}
        response = self.app.post('/songs/1/update', json=data, headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)

    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_delete_song(self, mock_session, mock_user_query, mock_song_query):
        mock_song_instance = MagicMock()
        mock_song_instance.user.username = 'testuser'
        mock_song_query.get.return_value = mock_song_instance

        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        response = self.app.post('/songs/1/delete', headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(response.json['message'], 'Song deleted successfully!')

    '''
    @patch('app_jsonified.ChatOpenAI')
    @patch('app_jsonified.User.query')
    def test_ai_song_suggestions(self, mock_user_query, mock_chat_openai):
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_chat_openai_instance = MagicMock()
        mock_chat_openai.return_value = mock_chat_openai_instance
        mock_chat_openai_instance.messages.return_value = {"content": "sample song recommendations"}

        response = self.app.get('/ai_song_suggestions/all-time/testuser', headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    '''
    '''
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    def test_list_songs(self, mock_user_query, mock_song_query):
        # Mock a song instance with JSON serializable attributes
        mock_song_instance = MagicMock()
        mock_song_instance.track_name = "Test Song"
        mock_song_instance.performer = "Test Artist"
        mock_song_instance.album = "Test Album"
        mock_song_instance.rating = 5
        mock_song_instance.username = "testuser"
        mock_song_instance.permission = True
        mock_song_instance.updated_at = datetime.utcnow()
        mock_song_query.filter_by.return_value.all.return_value = [mock_song_instance]

        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        response = self.app.get('/songs', query_string={'username': 'testuser'})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
    '''
    
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    def test_export_songs(self, mock_user_query, mock_song_query):
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_song_instance = MagicMock()
        mock_song_query.filter_by.return_value.all.return_value = [mock_song_instance]

        response = self.app.get('/export_songs', headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/csv')

    @patch('app_jsonified.User.query')
    def test_register_user_failure(self, mock_user_query):
        mock_user_instance = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance  # User already exists

        data = {'username': 'existinguser', 'password': 'password123'}
        response = self.app.post('/register', json=data)

        self.assertEqual(response.status_code, 409)  # Conflict - user already exists
        self.assertIn('error', response.json)
    
    @patch('app_jsonified.bcrypt.check_password_hash')
    @patch('app_jsonified.User.query')
    def test_login_failure(self, mock_user_query, mock_check_password_hash):
        mock_user_instance = MagicMock()
        mock_user_instance.password = 'hashed_password'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_check_password_hash.return_value = False  # Simulate password check failure

        data = {'username': 'user', 'password': 'incorrect_password'}
        response = self.app.post('/login', json=data)

        self.assertEqual(response.status_code, 401)  # Unauthorized
        self.assertIn('error', response.json)

    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_block_user(self, mock_session, mock_user_query):
        blocker = MagicMock()
        blocked = MagicMock()
        mock_user_query.get.side_effect = [blocker, blocked]

        data = {'blocker': 'user1', 'blocked': 'user2'}
        response = self.app.post('/block_friend', json=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(response.json['message'], 'user2 blocked')
        blocker.blocked.append.assert_called_with(blocked)
        mock_session.commit.assert_called_once()

    @patch('app_jsonified.Song.query')
    def test_filter_songs_by_performer(self, mock_song_query):
        mock_song_instance = MagicMock()
        mock_song_query.filter_by.return_value.filter.return_value.all.return_value = [mock_song_instance]

        response = self.app.get('/songs', query_string={'username': 'testuser', 'performer': 'Artist Name'})

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    @patch('app_jsonified.allowed_file')
    @patch('app_jsonified.User.query')
    def test_invalid_song_upload_file_type(self, mock_user_query, mock_allowed_file):
        mock_allowed_file.return_value = False  # Simulate invalid file type

        data = {'file': (BytesIO(b'sample,data'), 'test.invalid')}
        headers = {'Authorization': 'valid_token'}
        response = self.app.post('/upload_songs', data=data, content_type='multipart/form-data', headers=headers)

        self.assertEqual(response.status_code, 400)  # Bad request
        self.assertIn('error', response.json)

    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_delete_songs_by_album(self, mock_session, mock_user_query, mock_song_query):
        mock_user_instance = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_song_query.filter_by.return_value.all.return_value = [MagicMock()]

        response = self.app.post('/songs/album/AlbumName/delete', headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    @patch('app_jsonified.FriendRequest.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_respond_to_friend_request(self, mock_session, mock_user_query, mock_friend_request_query):
        mock_user_instance = MagicMock()
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance
        mock_friend_request = MagicMock()
        mock_friend_request_query.filter_by.return_value.first.return_value = mock_friend_request

        data = {'invite_id': 1, 'response': 'accept'}
        response = self.app.post('/respond_invite', json=data, headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
    
    @patch('app_jsonified.Song.query')
    @patch('app_jsonified.User.query')
    def test_update_song_rating_failure_unauthorized(self, mock_user_query, mock_song_query):
        mock_song_instance = MagicMock()
        mock_song_instance.user.username = 'other_user'
        mock_song_query.get.return_value = mock_song_instance

        data = {'new_rating': 4}
        response = self.app.post('/songs/1/update', json=data, headers={'Authorization': 'valid_token'})

        self.assertEqual(response.status_code, 404)  # Not found or unauthorized
        self.assertIn('error', response.json)





if __name__ == '__main__':
    unittest.main()
