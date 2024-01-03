from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import json
from werkzeug.utils import secure_filename
from sqlalchemy import MetaData, Table
from sqlalchemy import and_
from flask import Response, stream_with_context
from io import StringIO
from flask_bcrypt import Bcrypt
import secrets
from flask_cors import CORS
import spotifysearch
from spotifysearch.client import Client
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)


# Flask configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:backend777@35.240.109.106/tastetwister'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence the deprecation warning
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Your application's Client ID and Client Secret
SPOTIFY_CLIENT_ID = "8a9fb2659bdb46d6815580ec3ff4d2c6"
SPOTIFY_CLIENT_SECRET = "33868db571fc4139b13a265fef72d4ab"

db = SQLAlchemy(app)

friendships = db.Table('friendships',
    db.Column('user1', db.String(255), db.ForeignKey('users.username'), primary_key=True),
    db.Column('user2', db.String(255), db.ForeignKey('users.username'), primary_key=True)
)

class FriendRequest(db.Model):
    __tablename__ = 'friend_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    receiver = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'denied'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.Text, nullable=False)  # In a real-world app, hash the password
    token = db.Column(db.String(255), nullable=False)  # Assuming token should be non-nullable
    songs = db.relationship('Song', backref='user', lazy=True)
    permission = db.Column(db.Boolean, nullable=False)
    
    
    # Relationship for friendships
    friends = db.relationship('User', 
                            secondary=friendships,
                            primaryjoin=(friendships.c.user1 == username),
                            secondaryjoin=(friendships.c.user2 == username),
                            backref=db.backref('users', lazy='dynamic'),
                            lazy='dynamic')
    # Relationships for friend requests
    sent_requests = db.relationship('FriendRequest', foreign_keys=[FriendRequest.sender],
                                    backref='sender_user', lazy='dynamic')
    received_requests = db.relationship('FriendRequest', foreign_keys=[FriendRequest.receiver],
                                        backref='receiver_user', lazy='dynamic')

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    performer = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    permission = db.Column(db.Boolean, nullable=True)  # not planning to use null but just in case
    
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def update_rating(self, new_rating):
        self.rating = new_rating
        db.session.commit()



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_or_update_song(user_track_name, user_performer, user_album, rating, username):
    # Convert empty string in rating to None
    if rating == '':  # <-- This is the added line
        rating = None  # <-- This is the added line

    
    #Add a new song or update an existing one with verified information from Spotify.
    myclient = Client(SPOTIFY_CLIENT_ID , SPOTIFY_CLIENT_SECRET)
    search_result = myclient.search(user_track_name + " " + user_performer + " " + user_album)
    tracks = search_result.get_tracks()
    if tracks:
        track = tracks[0]
        # Now you can process the track as before
        track_name = track.name
        performer = track.artists[0].name
        album = track.album.name

        # Check if the song already exists in the database for this user
        existing_song = Song.query.filter_by(track_name=track_name, performer=performer, album=album, username=username).first()

        user = User.query.filter_by(username=username).first()
        permission = user.permission
        
        if existing_song:
            # Update the existing song with Spotify data
            existing_song.rating = rating  # Only the rating is updated as it's user-specific
        else:
            # Add a new song with Spotify data
            new_song = Song(track_name=track_name, performer=performer, album=album, rating=rating, username=username, permission=permission)
            db.session.add(new_song)
    else:
        # Handle the case when no tracks are found
        flash('No tracks found on Spotify with the provided details.', 'warning')
        # You can redirect the user or take any other action as required
    
    db.session.commit()

def add_songs_from_csv(file_path, username):
    invalid_rows = 0
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                track_name = row['track_name']
                performer = row['performer']
                album = row['album']
                if (row['rating'] == None):
                    rating = row['rating']
                else:
                    rating = int(row['rating'])
                
                # Validate rating range and that other fields are strings
                if (not isinstance(track_name, str) or 
                    not isinstance(performer, str) or 
                    not isinstance(album, str)):
                    raise ValueError
                
                if (rating != 1 and rating != 2 and rating != 3 and rating != 4 and rating != 5 and rating != None):
                    raise ValueError
                
                add_or_update_song(track_name, performer, album, rating, username)

            except (KeyError, ValueError):  
                invalid_rows += 1
                continue  # skips the current item and moves to the next

        db.session.commit()
        
        # Flash a message if some rows were skipped
        if invalid_rows > 0:
            flash('Some imports did not meet the required format', 'warning')

def add_songs_from_json(file_path, username):
    invalid_items = 0
    with open(file_path) as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            try:
                track_name = item['track_name']
                performer = item['performer']
                album = item['album']
                if (item['rating'] == None):
                    rating = item['rating']
                else:
                    rating = int(item['rating'])

                # Validate rating range and that other fields are strings
                if (not isinstance(track_name, str) or 
                    not isinstance(performer, str) or 
                    not isinstance(album, str)):
                    raise ValueError
                
                if (rating != 1 and rating != 2 and rating != 3 and rating != 4 and rating != 5 and rating != None):
                    raise ValueError
                
                add_or_update_song(track_name, performer, album, rating, username)

            except (KeyError, ValueError):  
                invalid_items += 1
                continue  # skips the current item and moves to the next

        db.session.commit()

        # Flash a message if some items were invalid
        if invalid_items > 0:
            flash('Some imports did not meet the required format', 'warning')


@app.route('/')
def home():
    return jsonify({'message': 'Welcome to TasteTwister'}), 200


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        unique_token = secrets.token_hex(16)
        permission = data.get('permission', False)  # we have no permission as default, shouldn't be a problem
        new_user = User(username=username, password=hashed_pw, token=unique_token, permission=permission)
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration successful!', 'token': unique_token}), 201
    
    return jsonify({'error': 'Invalid request method'}), 405


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Generate a new token
            new_token = secrets.token_hex(16)
            user.token = new_token
            db.session.commit()

            return jsonify({
                'message': 'Login successful!',
                'username': user.username,
                'token': new_token
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({'error': 'Invalid request method'}), 405


@app.route('/logout', methods=['POST'])
def logout():
    # Assuming the token is passed in the header of the request
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Find the user with the provided token
    user = User.query.filter_by(token=token).first()

    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Invalidate the token
    user.token = None
    db.session.commit()

    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/songs', methods=['GET', 'POST'])
def songs():
    # Handle GET requests
    if request.method == 'GET':
        username = request.args.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        songs = Song.query.filter_by(username=username).all()
        return jsonify([
        {
            "id": song.id,
            "track_name": song.track_name,
            "performer": song.performer,
            "album": song.album,
            "rating": song.rating,
            "permission": song.permission,
            "updated_at": song.updated_at  # Include the updated timestamp in the response
        } for song in songs
    ]), 200

    # Handle POST requests
    if request.method == 'POST':
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization token is required'}), 401

        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({'error': 'Invalid token'}), 401

        data = request.get_json()
        track_name = data.get('track_name')
        performer = data.get('performer')
        album = data.get('album')
        rating = data.get('rating')

        if not all([track_name, performer, album, rating]):
            return jsonify({'error': 'Missing song data'}), 400

        add_or_update_song(track_name, performer, album, rating, user.username)
        return jsonify({'message': 'Song added or updated!'}), 201

    # If method is neither GET nor POST
    return jsonify({'error': 'Invalid request method'}), 405

# Route for listing songs and adding the selected song
@app.route('/list_and_add_songs', methods=['POST'])
def list_and_add_songs():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.get_json()
    user_track_name = data.get('track_name')
    user_performer = data.get('performer')
    user_album = data.get('album')

    # Call the function to list the most relevant 5 songs based on user input
    relevant_songs = list_most_relevant_songs(user_track_name, user_performer, user_album)

    if not relevant_songs:
        return jsonify({'message': 'No relevant songs found'}), 200

    # Include user permission in the response if needed
    response_data = {'relevant_songs': relevant_songs}
    #response_data = {'relevant_songs': relevant_songs, 'user_permission': user.permission
    return jsonify(response_data), 200

# Route for adding the selected song
@app.route('/add_selected_song', methods=['POST'])
def add_selected_song():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.get_json()
    chosen_song_data = data.get('chosen_song')
    if not chosen_song_data:
        return jsonify({'error': 'Chosen song data is required'}), 400

    # Extract relevant information from the chosen song data
    chosen_track_name = chosen_song_data.get('track_name')
    chosen_performer = chosen_song_data.get('performer')
    chosen_album = chosen_song_data.get('album')
    rating = chosen_song_data.get('rating')

    # Check if the song already exists in the database for this user
    existing_song = Song.query.filter_by(track_name=chosen_track_name, performer=chosen_performer, album=chosen_album, username=user.username).first()

    if existing_song:
        # Update the existing song with a new rating
        existing_song.rating = rating
    else:
        # Add a new song with Spotify data and user rating
        new_song = Song(
            track_name=chosen_track_name,
            performer=chosen_performer,
            album=chosen_album,
            rating=rating,
            username=user.username,
            permission=user.permission
        )
        db.session.add(new_song)

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Chosen song added successfully!'}), 201

def list_most_relevant_songs(track_name, performer, album):
    # Use Spotify API to get the most relevant 5 songs
    myclient = Client(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
    search_result = myclient.search(track_name + " " + performer + " " + album)
    tracks = search_result.get_tracks()

    if tracks:
        relevant_songs = [
            {
                "track_name": track.name,
                "performer": track.artists[0].name,
                "album": track.album.name,
                "preview_url": track.preview_url,
            } for track in tracks[:5]
        ]
        return relevant_songs

    # If no tracks found, return an empty list
    return []

@app.route('/songs/unrated', methods=['GET'])
def get_unrated_songs():
    # Handle GET requests for unrated songs
    if request.method == 'GET':
        username = request.args.get('username')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        unrated_songs = Song.query.filter(Song.username == username, Song.rating.is_(None)).all()
        return jsonify([
            {
                "id": song.id,
                "track_name": song.track_name,
                "performer": song.performer,
                "album": song.album,
                "rating": song.rating,  # This will be None for unrated songs
                "permission": song.permission,
                "updated_at": song.updated_at  # Include the updated timestamp
            } for song in unrated_songs
        ]), 200




@app.route('/upload_songs', methods=['POST'])
def upload_songs():
    # Validate the token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 402

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Check if the file part is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']

    # Check if the filename is not empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validate file type and process accordingly
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        extension = filename.rsplit('.', 1)[1].lower()

        # Process based on file extension
        if extension == "csv":
            add_songs_from_csv(file_path, user.username)
        elif extension == "json":
            add_songs_from_json(file_path, user.username)

        return jsonify({'message': 'Songs uploaded successfully!'}), 200
    
    return jsonify({'error': 'Unsupported file type'}), 400


@app.route('/songs/<int:id>/update', methods=['POST'])
def update_song_rating(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    song = Song.query.get(id)
    if song and song.user.username == user.username:
        new_rating = request.get_json('new_rating')['new_rating']
        if new_rating:
            song.update_rating(new_rating)
            return jsonify({'message': 'Song rating updated successfully!'}), 200
        else:
            return jsonify({'error': 'New rating not provided'}), 400
    else:
        return jsonify({'error': 'Song not found or unauthorized access'}), 404

# Route for single entry deletion
@app.route('/songs/<int:id>/delete', methods=['POST'])
def delete_song(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    song = Song.query.get(id)
    if song and song.user.username == user.username:
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted successfully!'}), 200
    else:
        return jsonify({'error': 'Song not found or unauthorized access'}), 404

# Route for deletion by artist
@app.route('/songs/artist/<string:artist>/delete', methods=['POST'])
def delete_songs_by_artist(artist):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    songs_to_delete = Song.query.filter_by(username=user.username, performer=artist).all()
    if songs_to_delete:
        for song in songs_to_delete:
            db.session.delete(song)
        db.session.commit()
        return jsonify({'message': f'All songs by {artist} deleted successfully!'}), 200
    else:
        return jsonify({'error': 'No songs found for the specified artist or unauthorized access'}), 404

# Route for deletion by album
@app.route('/songs/album/<string:album>/delete', methods=['POST'])
def delete_songs_by_album(album):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    songs_to_delete = Song.query.filter_by(username=user.username, album=album).all()
    if songs_to_delete:
        for song in songs_to_delete:
            db.session.delete(song)
        db.session.commit()
        return jsonify({'message': f'All songs from the album {album} deleted successfully!'}), 200
    else:
        return jsonify({'error': 'No songs found for the specified album or unauthorized access'}), 404


'''
Now, you can call the export route with additional query parameters like so:
/export_songs?performer=Taylor Swift to get songs by Taylor Swift.
/export_songs?rating=5 to get songs with a rating of 5.
/export_songs?performer=Taylor Swift&rating=5 to get songs by Taylor Swift with a rating of 5.
'''
@app.route('/export_songs', methods=['GET'])
def export_songs():
    # Validate the token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Retrieve filter parameters from query string
    filter_performer = request.args.get('performer')
    filter_rating = request.args.get('rating')

    # Start with all songs for the user
    query = Song.query.filter_by(username=user.username)

    # Apply performer filter if provided
    if filter_performer:
        query = query.filter(Song.performer.ilike(f"%{filter_performer}%"))

    # Apply rating filter if provided and if it's a digit
    if filter_rating and filter_rating.isdigit():
        query = query.filter(Song.rating == int(filter_rating))

    songs = query.all()

    def generate():
        data = StringIO()
        w = csv.writer(data)

        # Write header
        w.writerow(('Track Name', 'Performer', 'Album', 'Rating'))
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # Write song data
        for song in songs:
            w.writerow((
                song.track_name,
                song.performer,
                song.album,
                song.rating
            ))
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # Add the appropriate headers and return the generated CSV data
    headers = {
        'Content-Disposition': 'attachment; filename=songs.csv',
        'Content-type': 'text/csv'
    }

    return Response(stream_with_context(generate()), headers=headers), 200



@app.route('/send_invite', methods=['POST'])
def send_invite():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    receiver_username = request.json.get('receiver')
    if current_user.username == receiver_username:
        return jsonify({'message': 'Cannot send invite to yourself'}), 400

    receiver = User.query.filter_by(username=receiver_username).first()
    if not receiver:
        return jsonify({'message': 'Receiver not found'}), 404

    # Check for existing friendship
    existing_friendship = db.session.query(friendships).filter(
        (friendships.c.user1 == current_user.username) & (friendships.c.user2 == receiver_username) |
        (friendships.c.user1 == receiver_username) & (friendships.c.user2 == current_user.username)
    ).first()

    if existing_friendship:
        return jsonify({'message': 'You are already friends'}), 400

    existing_request = FriendRequest.query.filter_by(sender=current_user.username, receiver=receiver_username).first()

    # Check if an existing request is 'denied', allow to send another invite
    if existing_request and existing_request.status != 'denied':
        return jsonify({'message': 'Invite already sent or pending'}), 400

    new_invite = FriendRequest(sender=current_user.username, receiver=receiver_username, status='pending')
    db.session.add(new_invite)
    db.session.commit()

    return jsonify({'message': 'Friend invite sent'}), 200



@app.route('/incoming_invites', methods=['GET'])
def view_incoming_invites():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    invites = FriendRequest.query.filter_by(receiver=current_user.username, status='pending').all()
    invites_data = [{'id': invite.id, 'sender': invite.sender, 'sent_at': invite.sent_at} for invite in invites]

    return jsonify(invites_data), 200



@app.route('/respond_invite', methods=['POST'])
def respond_invite():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    invite_id = request.json.get('invite_id')
    response = request.json.get('response')  # 'accept' or 'deny'

    invite = FriendRequest.query.filter_by(id=invite_id, receiver=current_user.username).first()
    if not invite:
        return jsonify({'message': 'Invite not found'}), 404

    if response == 'accept':
        # Add to friends
        sender_user = User.query.filter_by(username=invite.sender).first()
        if sender_user:
            # Insert entries into the friendships table
            current_user.friends.append(sender_user)
            sender_user.friends.append(current_user)
        else:
            return jsonify({'message': 'Sender not found'}), 404
    # Update invite status
    invite.status = 'accepted' if response == 'accept' else 'denied'
    invite.responded_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Invite responded'}), 200



@app.route('/friends/<username>', methods=['GET'])
def view_friends(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    friends = [friend.username for friend in user.friends]
    return jsonify(friends), 200


@app.route('/remove_friend', methods=['POST'])  # Changed from DELETE to POST
def remove_friend():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    friend_username = request.json.get('friend_username')
    friend = User.query.filter_by(username=friend_username).first()
    if not friend or friend not in current_user.friends:
        return jsonify({'message': 'Friend not found'}), 404

    current_user.friends.remove(friend)
    db.session.commit()

    return jsonify({'message': 'Friend removed'}), 200



@app.route('/recommend_playlist_all_users', methods=['GET'])
def recommend_playlist_all_users():
    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Extract additional query parameters
    username = user.username  # Assuming the username is derived from the authenticated user
    timeframe = request.args.get('timeframe', 'all-time')

    # Fetch 2 songs from the user with rating >= 4
    user_songs = Song.query.filter(
        Song.username == username, 
        Song.rating >= 4
    ).order_by(db.func.random()).limit(2).all()

    # Fetch 8 songs from other users with rating >= 4
    query = Song.query.filter(
        Song.username != username, 
        Song.permission.is_(True), 
        Song.rating >= 4
    )
    if timeframe == 'recent':
        recent_time = datetime.now() - timedelta(hours=24)
        query = query.filter(Song.updated_at >= recent_time)

    other_songs = query.order_by(db.func.random()).limit(8).all()

    # Combine songs to create the playlist
    playlist = user_songs + other_songs

    # Randomize the order of the songs in the playlist
    random.shuffle(playlist)

    # Convert songs to JSON format
    playlist_json = [{
        "id": song.id,
        "track_name": song.track_name,
        "performer": song.performer,
        "album": song.album,
        "rating": song.rating,
        "username": song.username,
        "permission": song.permission,
        "updated_at": song.updated_at
    } for song in playlist]

    return jsonify(playlist_json), 200

@app.route('/recommend_playlist_friends_duo', methods=['GET'])
def recommend_playlist_friends_duo():
    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    friend_username = request.args.get('friend_username')
    if not friend_username:
        return jsonify({'error': 'Friend username is required'}), 400

    # Check if friend user exists and if they are friends
    friend = User.query.filter_by(username=friend_username).first()
    if not friend or friend not in user.friends:
        return jsonify({'error': 'Friend not found or users are not friends'}), 404

    # Extract timeframe from query parameters
    timeframe = request.args.get('timeframe', 'all-time')

    # Define a base query for fetching songs
    base_query = lambda username: Song.query.filter(
        Song.username == username, 
        Song.rating >= 4
    )

    # Apply timeframe filter if needed
    if timeframe == 'recent':
        recent_time = datetime.now() - timedelta(hours=24)
        user_songs_query = base_query(user.username).filter(Song.updated_at >= recent_time)
        friend_songs_query = base_query(friend_username).filter(Song.updated_at >= recent_time)
    else:
        user_songs_query = base_query(user.username)
        friend_songs_query = base_query(friend_username)

    # Fetch songs with random order and limit
    user_songs = user_songs_query.order_by(db.func.random()).limit(5).all()
    friend_songs = friend_songs_query.order_by(db.func.random()).limit(5).all()

    # Combine and shuffle the playlist
    playlist = user_songs + friend_songs
    random.shuffle(playlist)

    # Convert to JSON
    playlist_json = [{
        "id": song.id,
        "track_name": song.track_name,
        "performer": song.performer,
        "album": song.album,
        "rating": song.rating,
        "username": song.username,
        "permission": song.permission,
        "updated_at": song.updated_at
    } for song in playlist]

    return jsonify(playlist_json), 200



@app.route('/recommend_playlist_from_all_friends', methods=['GET'])
def recommend_playlist_from_all_friends():
    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Extract timeframe from query parameters
    timeframe = request.args.get('timeframe', 'all-time')

    # Define a base query for fetching songs
    base_query = lambda username: Song.query.filter(
        Song.username == username, 
        Song.rating >= 4
    )

    # Apply timeframe filter if needed
    if timeframe == 'recent':
        recent_time = datetime.now() - timedelta(hours=24)
        user_songs_query = base_query(user.username).filter(Song.updated_at >= recent_time)
        friend_songs_query = Song.query.join(
            User, User.username == Song.username
        ).filter(
            User.username != user.username, 
            User.username.in_([friend.username for friend in user.friends]), 
            Song.rating >= 4,
            Song.updated_at >= recent_time
        )
    else:
        user_songs_query = base_query(user.username)
        friend_songs_query = Song.query.join(
            User, User.username == Song.username
        ).filter(
            User.username != user.username, 
            User.username.in_([friend.username for friend in user.friends]), 
            Song.rating >= 4
        )

    # Fetch songs with random order and limit
    user_songs = user_songs_query.order_by(db.func.random()).limit(2).all()
    friend_songs = friend_songs_query.order_by(db.func.random()).limit(8).all()

    # Combine and shuffle the playlist
    playlist = user_songs + friend_songs
    random.shuffle(playlist)

    # Convert to JSON
    playlist_json = [{
        "id": song.id,
        "track_name": song.track_name,
        "performer": song.performer,
        "album": song.album,
        "rating": song.rating,
        "username": song.username,
        "permission": song.permission,
        "updated_at": song.updated_at
    } for song in playlist]

    return jsonify(playlist_json), 200


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

# This section will create all tables in the database if they don't exist.
with app.app_context():
    db.create_all()