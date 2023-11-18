from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import json
from werkzeug.utils import secure_filename
from sqlalchemy import MetaData, Table
from flask import Response, stream_with_context
from io import StringIO
from flask_bcrypt import Bcrypt
import secrets
from flask_cors import CORS
import spotifysearch
from spotifysearch.client import Client
from datetime import datetime


app = Flask(_name_)
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
    _tablename_ = 'users'
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
    _tablename_ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    performer = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    permission = db.Column(db.Boolean, nullable=True)  # not planning to use null but just in case
    
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
            "permission": song.permission  # Include permission in the response
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
                "rating": song.rating  # This will be None
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


if _name_ == '_main_':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

# This section will create all tables in the database if they don't exist.
with app.app_context():
    db.create_all()