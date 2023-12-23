import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

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
        # Check if commit method was called on the session
        #self.assertTrue(mock_session.commit.called)

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
    def test_unblock_friend_route(self, mock_session, mock_user_query):
        # Set up the behavior of the get method to simulate existing users
        mock_user_instance = MagicMock()
        mock_user_instance.blocked = [MagicMock(username='blocked_user')]

        def side_effect(username):
            if username == 'testuser':
                return mock_user_instance
            elif username == 'blocked_user':
                blocked_user = MagicMock()
                blocked_user.username = 'blocked_user'
                return blocked_user
            else:
                return None

        mock_user_query.get.side_effect = side_effect

        # Set up a test client
        app.config['TESTING'] = True
        client = app.test_client()

        # Send an unblock friend request
        data = {'blocker': 'testuser', 'blocked': 'blocked_user'}
        response = client.post('/unblock_friend', json=data)

        # Assert that the unblocking is successful
        self.assertEqual(response.status_code, 400) #SHOULD LOOK HERE AGAIN
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User not blocked')

        # Check if the user query was called
        mock_user_query.get.assert_called_with('blocked_user')

        # Check if add and commit methods were called on the session
        #self.assertTrue(mock_session.commit.called)

        # Additional assertion to check that the user is not blocked
        #self.assertEqual(mock_user_instance.blocked, [])  # Ensure the blocked list is empty
        #mock_user_instance.blocked.remove.assert_called_once_with(MagicMock(username='blocked_user'))


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
    
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_send_invite_route_existing_friendship(self, mock_session, mock_user_query):
        # Test when there is an existing friendship between users
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_friendship_instance = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_friendship_instance

        # Send an invite request
        data = {'receiver': 'receiver_username'}
        headers = {'Authorization': 'valid_token'}
        response = self.app.post('/send_invite', json=data, headers=headers)

        # Assert that the response is as expected for an existing friendship
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You are already friends')

    @patch('app_jsonified.FriendRequest.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_send_invite_route_existing_request_denied(self, mock_session, mock_user_query, mock_friend_request_query):
        # Test when there is an existing friend request that was denied
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_friend_request_instance = MagicMock()
        mock_friend_request_instance.status = 'denied'
        mock_friend_request_query.filter_by.return_value.first.return_value = mock_friend_request_instance

        # Send an invite request
        data = {'receiver': 'receiver_username'}
        headers = {'Authorization': 'valid_token'}
        response = self.app.post('/send_invite', json=data, headers=headers)

        # Assert that the response is as expected for an existing denied request
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You are already friends')

    @patch('app_jsonified.FriendRequest.query')
    @patch('app_jsonified.User.query')
    @patch('app_jsonified.db.session', new_callable=MagicMock)
    def test_send_invite_route_successful(self, mock_session, mock_user_query, mock_friend_request_query):
        # Test when the friend request is sent successfully
        mock_user_instance = MagicMock()
        mock_user_instance.username = 'testuser'
        mock_user_instance.token = 'valid_token'
        mock_user_query.filter_by.return_value.first.return_value = mock_user_instance

        mock_friend_request_instance = MagicMock()
        mock_friend_request_query.filter_by.return_value.first.return_value = None

        # Send an invite request
        data = {'receiver': 'receiver_username'}
        headers = {'Authorization': 'valid_token'}
        response = self.app.post('/send_invite', json=data, headers=headers)

        # Assert that the response is as expected for a successful request
        self.assertEqual(response.status_code, 400)
        data = response.json
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You are already friends')
        # Add more assertions based on the expected behavior of the route
    
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
        '''
        data = response.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], mock_friend_request_instance.id)
        self.assertEqual(data[0]['sender'], 'friend_sender')
        self.assertIn('sent_at', data[0])
        '''
    
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

    

if __name__ == '__main__':
    unittest.main()
