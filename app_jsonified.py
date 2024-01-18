from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import json
from werkzeug.utils import secure_filename
from sqlalchemy import MetaData, Table, func, extract, desc
from sqlalchemy import and_, or_
from sqlalchemy.sql import and_, not_
from sqlalchemy.exc import SQLAlchemyError
from flask import Response, stream_with_context
from io import StringIO
from flask_bcrypt import Bcrypt
import secrets
from flask_cors import CORS
import spotifysearch
from spotifysearch.client import Client
from datetime import datetime, timedelta
import random
import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyOAuth, Spotify
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import re
import tempfile

app = Flask(__name__)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)


# Flask configurations

scope="playlist-read-private"
SPOTIPY_CLIENT_ID='bbdfbe5f9eff4726bcfed53dd23fd7bc'
SPOTIPY_CLIENT_SECRET='083c4ad6e42745f2809a3624f2e51de7'
SPOTIPY_REDIRECT_URI='https://google.com/callback/'

os.environ["SPOTIPY_CLIENT_ID"] = SPOTIPY_CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIPY_CLIENT_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = SPOTIPY_REDIRECT_URI

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
client_credentials_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


os.environ["SPOTIPY_CLIENT_ID"] = SPOTIPY_CLIENT_ID
os.environ["SPOTIPY_CLIENT_SECRET"] = SPOTIPY_CLIENT_SECRET
os.environ["SPOTIPY_REDIRECT_URI"] = SPOTIPY_REDIRECT_URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:backend777@35.240.109.106/tastetwister'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence the deprecation warning
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
ALLOWED_EXTENSIONS = {'csv', 'json'}

SPOTIFY_CLIENT_ID='bbdfbe5f9eff4726bcfed53dd23fd7bc'
SPOTIFY_CLIENT_SECRET='083c4ad6e42745f2809a3624f2e51de7'
SPOTIFY_REDIRECT_URI='https://google.com/callback/'

os.environ["OPENAI_API_KEY"] = "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"

def extract_music_info_from_results(results):
    songs = []
    for item in results['tracks']['items']:
        track = item['track']
        song_name = track['name']
        album_name = track['album']['name']
        performer = ', '.join([artist['name'] for artist in track['artists']])  # Join artist names
        songs.append({
            'track_name': song_name,
            'album': album_name,
            'performer': performer  # Now a string
        })
    return songs  # Returns a list of dictionaries


db = SQLAlchemy(app)

# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize the Chat model
chat = ChatOpenAI(api_key = "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", temperature=0.9, model="gpt-3.5-turbo")



friendships = db.Table('friendships',
    db.Column('user1', db.String(255), db.ForeignKey('users.username'), primary_key=True),
    db.Column('user2', db.String(255), db.ForeignKey('users.username'), primary_key=True)
)

blocked_users = db.Table('blocked_users',
    db.Column('blocker', db.String(255), db.ForeignKey('users.username'), primary_key=True),
    db.Column('blocked', db.String(255), db.ForeignKey('users.username'), primary_key=True)
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
    
    # Relationship for blocked users
    blocked = db.relationship('User', 
                            secondary=blocked_users,
                            primaryjoin=(blocked_users.c.blocker == username),
                            secondaryjoin=(blocked_users.c.blocked == username),
                            backref=db.backref('blocked_by', lazy='dynamic'),
                            lazy='dynamic')


class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    performer = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    permission = db.Column(db.Boolean, nullable=True)  # not planning to use null but just in case
    
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def update_rating(self, new_rating):
        self.rating = new_rating
        db.session.commit()


def add_or_update_song(user_track_name, user_performer, user_album, rating, username):
    # Convert empty string in rating to None
    if rating == '':
        rating = None

    # Check if the song already exists in the database for this user
    existing_song = Song.query.filter_by(track_name=user_track_name, performer=user_performer, album=user_album, username=username).first()

    user = User.query.filter_by(username=username).first()
    permission = user.permission

    if existing_song:
        # Update the existing song with user-provided data
        existing_song.rating = rating  # Only the rating is updated as it's user-specific
    else:
        # Add a new song with user-provided data
        new_song = Song(track_name=user_track_name, performer=user_performer, album=user_album, rating=rating, username=username, permission=permission)
        db.session.add(new_song)

    db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    #user.token = None
    #db.session.commit()

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
    # Does not have token authentication because of seeing friends songs logic
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

        if not all([track_name, performer, album]):
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
            } for track in tracks[:5]
        ]
        return relevant_songs

    # If no tracks found, return an empty list
    return []


# Does not have token authentication because of seeing friends songs logic
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


# Route for getting user's top 3 artists and their songs
@app.route('/get_top_artists_and_songs', methods=['GET'])
def get_top_artists_and_songs():
    # Validate the token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Get the user's top 3 artists and their songs
    recommendations = get_user_top_artists_and_songs(user.username)

    return jsonify(recommendations), 200


def get_user_top_artists_and_songs(username):
    # Query the database to get the user's top 3 artists and their songs based on ratings average
    top_artists_and_songs = db.session.query(Song.performer, func.avg(Song.rating).label('avg_rating')) \
        .filter(Song.username == username) \
        .group_by(Song.performer) \
        .order_by(desc('avg_rating')) \
        .limit(3) \
        .all()

    result = []
    for artist, _ in top_artists_and_songs:
        recommendations = get_recommendations_for_artists(username, [artist])
        result.extend(recommendations)

    return result


def get_recommendations_for_artists(username, artists):
    all_recommendations = []

    myclient = Client(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)

    for artist in artists:
        search_result = myclient.search(artist)
        tracks = search_result.get_tracks()

        if tracks:
            # Get songs that the user has already rated by the specified artist
            user_rated_songs = db.session.query(Song.track_name).filter(
                Song.username == username,
                Song.performer == artist
            ).all()

            unrated_songs = Song.query.filter(Song.username == username, Song.rating.is_(None)).all()

            # Filter out songs that the user has already rated
            recommendations = [
                {
                    "track_name": track.name,
                    "performer": track.artists[0].name,
                    "album": track.album.name,
                } for track in tracks[:5] if track.name not in [song.track_name for song in user_rated_songs] and track.name not in [song.track_name for song in unrated_songs]
            ]

            all_recommendations.extend(recommendations)

    return all_recommendations


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


@app.route('/outgoing_invites', methods=['GET'])
def view_outgoing_invites():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    # Fetch all pending invites sent by the current user
    invites = FriendRequest.query.filter_by(sender=current_user.username, status='pending').all()
    invites_data = [{'id': invite.id, 'receiver': invite.receiver, 'sent_at': invite.sent_at} for invite in invites]

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


# Not tokenized due to friend list viewing capability at profiles
@app.route('/friends/<username>', methods=['GET'])
def view_friends(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    friends = [friend.username for friend in user.friends]
    return jsonify(friends), 200


@app.route('/remove_friend', methods=['POST']) 
def remove_friend():
    token = request.headers.get('Authorization')
    current_user = User.query.filter_by(token=token).first()
    if not current_user:
        return jsonify({'error': 'Invalid token'}), 401

    friend_username = request.json.get('friend_username')
    friend = User.query.filter_by(username=friend_username).first()
    if not friend:
        return jsonify({'message': 'Friend not found'}), 404

    # Check if the friend is in the current user's friends list
    if friend not in current_user.friends:
        return jsonify({'message': 'Friend not found in your friend list'}), 404

    # Remove the friend from the current user's list
    current_user.friends.remove(friend)

    # Also remove the current user from the friend's list
    if current_user in friend.friends:
        friend.friends.remove(current_user)

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

    # Fetch songs from other users, excluding user's songs and blocked users
    user_songs = [(song.track_name, song.album) for song in user.songs]
    blocked_users = [blocked_user.username for blocked_user in user.blocked_by]

    # Create a list of conditions to exclude each song in user_songs
    exclusion_conditions = [and_(Song.track_name == track_name, Song.album == album) for track_name, album in user_songs]

    query = Song.query.filter(
        Song.username != user.username,
        Song.permission.is_(True),
        Song.rating >= 4,
        not_(or_(*exclusion_conditions)),  # Exclude songs in user_songs
        not_(Song.username.in_(blocked_users))
    )

    # Extract timeframe from query parameters
    timeframe = request.args.get('timeframe', 'all-time')
    if timeframe == 'recent':
        recent_time = datetime.now() - timedelta(hours=24)
        query = query.filter(Song.updated_at >= recent_time)

    # Fetch 10 songs with random order
    other_songs = query.order_by(db.func.random()).limit(10).all()

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
    } for song in other_songs]

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

    # Check if either user has blocked the other
    if user in friend.blocked or friend in user.blocked:
        return jsonify({'error': 'Cannot create playlist as one user has blocked the other'}), 403

    # Extract timeframe from query parameters
    timeframe = request.args.get('timeframe', 'all-time')

    # Define a base query for fetching songs
    def base_query(username):
        return Song.query.filter(
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

    # Filter out duplicate songs
    unique_songs = set()
    combined_playlist = []

    for song_list in [user_songs, friend_songs]:
        for song in song_list:
            song_identity = (song.track_name, song.album)
            if song_identity not in unique_songs:
                unique_songs.add(song_identity)
                combined_playlist.append(song)
            else:
                # Fetch an additional unique song
                additional_song = base_query(song.username).filter(
                    db.and_(Song.track_name, Song.album).notin_(unique_songs)
                ).order_by(db.func.random()).first()
                if additional_song:
                    unique_songs.add((additional_song.track_name, additional_song.album))
                    combined_playlist.append(additional_song)

    # Shuffle the playlist
    random.shuffle(combined_playlist)

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
    } for song in combined_playlist]

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

    # Fetch songs from friends, excluding user's songs and blocked users
    user_songs = [(song.track_name, song.album) for song in user.songs]
    blocked_users = [blocked_user.username for blocked_user in user.blocked_by]
    friend_usernames = [friend.username for friend in user.friends if friend.username not in blocked_users]

    # Create a list of conditions to exclude each song in user_songs
    exclusion_conditions = [and_(Song.track_name == track_name, Song.album == album) for track_name, album in user_songs]

    query = Song.query.filter(
        Song.username.in_(friend_usernames),
        Song.rating >= 4,
        not_(or_(*exclusion_conditions))  # Exclude songs in user_songs
    )

    # Extract timeframe from query parameters
    timeframe = request.args.get('timeframe', 'all-time')
    if timeframe == 'recent':
        recent_time = datetime.now() - timedelta(hours=24)
        query = query.filter(Song.updated_at >= recent_time)

    # Fetch 10 songs with random order
    friend_songs = query.order_by(db.func.random()).limit(10).all()

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
    } for song in friend_songs]

    return jsonify(playlist_json), 200


def filter_songs_by_timeframe(query, timeframe):
    if timeframe == 'last_24_hours':
        query = query.filter(Song.updated_at >= datetime.now() - timedelta(hours=24))
    elif timeframe == 'last_7_days':
        query = query.filter(Song.updated_at >= datetime.now() - timedelta(days=7))
    return query


def get_top_albums_or_performers(query, attribute):
    return (query.with_entities(attribute, func.avg(Song.rating).label('average_rating'))
            .group_by(attribute)
            .order_by(func.avg(Song.rating).desc())
            .limit(10)
            .all())


@app.route('/stats/all-time/<username>', methods=['GET'])
@app.route('/stats/last-7-days/<username>', methods=['GET'])
@app.route('/stats/last-24-hours/<username>', methods=['GET'])
def user_stats(username):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    timeframe = request.path.split('/')[2].replace('-', '_')
    songs_query = Song.query.filter_by(username=username)
    songs_query = filter_songs_by_timeframe(songs_query, timeframe)

    # Top 10 songs
    top_songs = (songs_query.order_by(Song.rating.desc())
                 .limit(10)
                 .all())
    top_songs_data = [{'id': song.id, 'track_name': song.track_name, 'rating': song.rating} for song in top_songs]

    # Top 10 albums
    top_albums = get_top_albums_or_performers(songs_query, Song.album)
    top_albums_data = [{'album': album[0], 'average_rating': album[1]} for album in top_albums]

    # Top 10 performers
    top_performers = get_top_albums_or_performers(songs_query, Song.performer)
    top_performers_data = [{'performer': performer[0], 'average_rating': performer[1]} for performer in top_performers]

    return jsonify({
        'top_songs': top_songs_data,
        'top_albums': top_albums_data,
        'top_performers': top_performers_data
    }), 200


def get_filtered_songs_stats(query, timeframe, username, filter_by=None, filter_value=None):
    # Filter by timeframe
    if timeframe == 'last_24_hours':
        time_threshold = datetime.now() - timedelta(hours=24)
    elif timeframe == 'last_7_days':
        time_threshold = datetime.now() - timedelta(days=7)
    else:
        time_threshold = None

    if time_threshold:
        query = query.filter(Song.updated_at >= time_threshold)

    # Additional filtering by album or performer
    if filter_by and filter_value:
        if filter_by == 'album':
            query = query.filter(Song.album == filter_value)
        elif filter_by == 'performer':
            query = query.filter(Song.performer == filter_value)
    
    # Filter by username
    query = query.filter(Song.username == username)

    # Group by day and calculate average rating per day
    grouped_query = (query.with_entities(
                        func.date(Song.updated_at).label('date'),
                        func.avg(Song.rating).label('avg_rating'))
                    .group_by('date')
                    .order_by('date'))

    daily_avg_ratings = {}
    for row in grouped_query.all():
        daily_avg_ratings[row.date.isoformat()] = float(row.avg_rating)

    # Overall mean rating for the timeframe
    mean_rating = query.with_entities(func.avg(Song.rating)).scalar()

    return mean_rating, daily_avg_ratings


@app.route('/stats/mean/all-time', methods=['GET'])
@app.route('/stats/mean/last-7-days', methods=['GET'])
@app.route('/stats/mean/last-24-hours', methods=['GET'])
def mean_stats():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    timeframe = request.path.split('/')[3].replace('-', '_')
    username = request.args.get('username')  # To get the username parameter
    filter_by = request.args.get('filter_by')  # 'album' or 'performer'
    filter_value = request.args.get('filter_value')  # Name of the album or performer

    query = Song.query
    mean_rating, daily_avg_ratings = get_filtered_songs_stats(query, timeframe, username, filter_by, filter_value)

    return jsonify({
        'mean_rating': mean_rating,
        'daily_average_ratings': daily_avg_ratings
    }), 200

@app.route('/block_friend', methods=['POST'])
def block_friend():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.json
    blocker_username = data.get('blocker')
    blocked_username = data.get('blocked')
    try:
        blocker = User.query.get(blocker_username)
        blocked = User.query.get(blocked_username)

        if not blocker or not blocked:
            return jsonify({"message": "User not found"}), 404

        # Check if they are already blocked
        if blocked in blocker.blocked:
            return jsonify({"message": "User already blocked"}), 400

        # Add to blocked list
        blocker.blocked.append(blocked)
        db.session.commit()

        return jsonify({"message": f"{blocked_username} blocked"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/unblock_friend', methods=['POST'])
def unblock_friend():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    data = request.json
    blocker_username = data.get('blocker')
    blocked_username = data.get('blocked')


    try:
        blocker = User.query.get(blocker_username)
        blocked = User.query.get(blocked_username)

        if not blocker or not blocked:
            return jsonify({"message": "User not found"}), 404

        # Check if they are blocked
        if blocked not in blocker.blocked:
            return jsonify({"message": "User not blocked"}), 400

        # Remove from blocked list
        blocker.blocked.remove(blocked)
        db.session.commit()

        return jsonify({"message": f"{blocked_username} unblocked"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/blocked_friends', methods=['GET'])
def view_blocked_friends():
    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Fetch blocked friends for the user
    blocked_friends = user.blocked.all()

    # Convert blocked friends to JSON format
    blocked_friends_data = [{'username': friend.username} for friend in blocked_friends]

    return jsonify(blocked_friends_data), 200


# Function to process the user input into the required format
def process_user_input(user_input):
    songs = user_input.split("\n")
    formatted_songs = "\n".join([f"- {song}" for song in songs])
    return formatted_songs

# Template for processing the list of songs
song_suggestion_template = """
Given the following list of songs, suggest 20 unique and creative songs that the user might enjoy. 
The suggestions can be from an artist not already mentioned and should offer a fresh perspective or unique style that could appeal to a fan of the listed songs. 
Consider less mainstream options and focus on diverse musical elements like unique beats, instruments, or lyrical themes.
Try to be as creative as possible, do not be repetitive.
Be mindful of the genre of these songs, and try to keep your suggestion in that genre as well.

Format the output as JSON with the strictly following keys: track_name, performer, album


{example}

User's favorite songs:
{songs}
"""

example =  """

Example format of return:

{ "track_name": "Trouble", "performer": "Taylor Swift", "album": "Trouble" }

{ "track_name": "Bad Boy", "performer": "Red Velvet", "album": "The Perfect Velvet" }

"""


@app.route('/ai_song_suggestions/all-time/<username>', methods=['GET'])
@app.route('/ai_song_suggestions/last-7-days/<username>', methods=['GET'])
@app.route('/ai_song_suggestions/last-24-hours/<username>', methods=['GET'])
def ai_song_suggestions(username):
    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    # Check if the authenticated user is the same as the one in the URL
    if authenticated_user.username != username:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Determine the timeframe from the request path
    timeframe = request.path.split('/')[2].replace('-', '_')

    # Query for top 10 songs based on the timeframe for the user
    songs_query = Song.query.filter_by(username=username)
    songs_query = filter_songs_by_timeframe(songs_query, timeframe)
    top_songs = (songs_query.order_by(Song.rating.desc())
                 .limit(10)
                 .all())

    # Format the top songs for the LLM input
    user_input = "\n".join([f"{song.track_name}, {song.performer}, {song.album}" for song in top_songs])
    #formatted_songs = process_user_input(user_input)

    # Creating the prompt message
    prompt_template = ChatPromptTemplate.from_template(song_suggestion_template)
    messages = prompt_template.format_messages(songs=user_input, example = example)

    # Getting the response
    response = chat(messages)

    response_content = response.content

    # Split the response into individual song strings
    song_strings = response_content.split('\n')

    # Parse each song string into a dictionary
    songs_list = []
    for song_str in song_strings:
        try:
            song_dict = json.loads(song_str)
            songs_list.append(song_dict)
        except json.JSONDecodeError:
            # Handle the case where the string is not a valid JSON
            continue

    # Return the list of songs as a JSON response
    return jsonify(songs_list)


# Template for processing the list of songs with era and genre
song_suggestion_era_genre_template = """
Suggest 20 unique and creative songs that the user might enjoy. 
The suggestions should reflect the musical styles and trends of the specified era and genre. 
Focus on diverse musical elements unique to the era/genre like beats, instruments, or lyrical themes.
The suggestions can be from artists known for their work in the specified era and genre.
Be creative and avoid repetition.

The suggested songs must be strictly from:
{era}

{genre}

Format the output as JSON with the strictly following keys: track_name, performer, album

Example format of return:

{example}

"""

@app.route('/ai_song_suggestions_by_era_genre/<username>', methods=['GET'])
def ai_song_suggestions_by_era_genre(username):
    era = request.args.get('era', default="")
    genre = request.args.get('genre', default="")

    if (era != ""):
        era += " Era"
        
    if (genre != ""):
        genre += " Genre"

    # Retrieve token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    # Authenticate user based on the token
    authenticated_user = User.query.filter_by(token=token).first()
    if not authenticated_user:
        return jsonify({'error': 'Invalid token'}), 401

    # Check if the authenticated user is the same as the one in the URL
    if authenticated_user.username != username:
        return jsonify({'error': 'Unauthorized access'}), 403

    # Create the prompt with era and genre
    #prompt = song_suggestion_era_genre_template.format(era = era, genre = genre)

    prompt_template = ChatPromptTemplate.from_template(song_suggestion_era_genre_template)
    messages = prompt_template.format_messages(era = era, genre = genre, example = example)

    # Get the response from the LLM
    response = chat(messages)

    response_content = response.content

    # Split the response into individual song strings
    song_strings = response_content.split('\n')

    # Parse each song string into a dictionary
    songs_list = []
    for song_str in song_strings:
        try:
            song_dict = json.loads(song_str)
            songs_list.append(song_dict)
        except json.JSONDecodeError:
            # Handle the case where the string is not a valid JSON
            continue

    # Return the list of songs as a JSON response
    return jsonify(songs_list)


@app.route('/unheard_artists', methods=['GET'])
def find_unheard_artists():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    one_week_ago = datetime.utcnow() - timedelta(days=7)

    artists = Song.query.with_entities(Song.performer)\
        .filter(
            Song.username == user.username,
            Song.updated_at < one_week_ago,
            not_(db.session.query(Song.id)
                 .filter(Song.performer == Song.performer,
                         Song.updated_at >= one_week_ago)
                 .exists())
        ).subquery()

    artist_song = Song.query.with_entities(Song.performer, Song.track_name)\
        .filter(
            Song.performer.in_(artists),
            Song.rating == 5
        ).order_by(func.random()).first()

    if artist_song:
        artist, song = artist_song
        return jsonify({'artist': artist, 'song': song}), 200
    else:
        return jsonify({}), 200


@app.route('/import_spotify_playlist', methods=['POST'])
def import_spotify_playlist():
    # Validate the token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is required'}), 402

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # Retrieve the playlist URL from the request
    data = request.json
    playlist_url = data.get('playlist_url')
    if not playlist_url:
        return jsonify({'error': 'Playlist URL is required'}), 400

    # Extract the playlist ID from the URL
    match = re.search(r"playlist\/([0-9A-Za-z]+)", playlist_url)
    if not match:
        return jsonify({'error': 'Invalid playlist URL'}), 400

    playlist_id = match.group(1)

    # Fetch the playlist data using the Spotify API
    try:
        results = sp.playlist(playlist_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Extract music information
    extracted_songs = extract_music_info_from_results(results)

    # Initialize count for invalid items
    invalid_items = 0

    # Iterate through the songs and add or update each
    for song in extracted_songs:
        try:
            track_name = song['track_name']
            performer = song['performer']
            album = song['album']

            # Validate that the fields are strings
            if not all(isinstance(field, str) for field in [track_name, performer, album]):
                raise ValueError("Invalid data type for song fields.")

            # Add or update the song in the database
            add_or_update_song(track_name, performer, album, None, user.username)

        except (KeyError, ValueError) as e:
            invalid_items += 1
            # Optionally log the error or error message
            # print("Error processing song:", e)
            continue

    # Commit changes to the database
    db.session.commit()

    # Flash a message if some items were invalid
    if invalid_items > 0:
        flash(f'{invalid_items} imports did not meet the required format', 'warning')

    return jsonify({'message': 'Playlist uploaded successfully!'}), 200




# This section will create all tables in the database if they don't exist.
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)