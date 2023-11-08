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
import requests
from requests.auth import HTTPBasicAuth
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import base64
import spotifysearch
from spotifysearch.client import Client

app = Flask(__name__)
bcrypt = Bcrypt(app)


# Flask configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:backend777@35.240.109.106/tastetwister'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence the deprecation warning
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to save uploaded files
ALLOWED_EXTENSIONS = {'csv', 'json'}


db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.Text, nullable=False)  # In a real-world app, hash the password
    songs = db.relationship('Song', backref='user', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    performer = db.Column(db.String(255), nullable=False)
    album = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(255), db.ForeignKey('users.username'), nullable=False)
    
    def update_rating(self, new_rating):
        self.rating = new_rating
        db.session.commit()


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('songs'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')  # Hash the password
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):  # Check hashed password
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('songs'))
        else:
            flash('Login failed! Check your credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/songs', methods=['GET', 'POST'])
def songs():
    if 'username' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.headers.get('Content-Type') == 'application/json':
            data = request.json
            track_name = data['track_name']
            performer = data['performer']
            album = data['album']
            rating = data['rating']
        else:
            track_name = request.form['track_name']
            performer = request.form['performer']
            album = request.form['album']
            rating = request.form['rating']

        # Use the helper function to add or update the song
        add_or_update_song(track_name, performer, album, rating, session['username'])

        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"message": "Song added or updated!"}), 201
        else:
            return redirect(url_for('songs'))

    songs = Song.query.filter_by(username=session['username']).all()
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify([
            {
                "id": song.id,
                "track_name": song.track_name,
                "performer": song.performer,
                "album": song.album,
                "rating": song.rating
            } for song in songs
        ])
    else:
        return render_template('index.html', songs=songs)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Your application's Client ID and Client Secret
SPOTIFY_CLIENT_ID = "8a9fb2659bdb46d6815580ec3ff4d2c6"
SPOTIFY_CLIENT_SECRET = "33868db571fc4139b13a265fef72d4ab"

def add_or_update_song(user_track_name, user_performer, user_album, rating, username):
    """
    Add a new song or update an existing one with information from Spotify.
    If the song is found on Spotify, use the Spotify data to add to the database.
    If the song is not found, inform the user and do not add to the database.
    """
    # Initialize variables with user input as default
    track_name = str(user_track_name)
    performer = str(user_performer)
    album = user_album

    myclient = Client(SPOTIFY_CLIENT_ID , SPOTIFY_CLIENT_SECRET)
    track = myclient.search(user_track_name + user_performer).get_tracks()[0]
    
    track_name = track.name
    performer = track.artists[0].name
    album =  track.album.name

    # Check if the song already exists in the database for this user
    existing_song = Song.query.filter_by(track_name=track_name, performer=performer, album=album, username=username).first()
    
    if existing_song:
        # Update the existing song with Spotify data
        existing_song.rating = rating  # Only the rating is updated as it's user-specific
    else:
        # Add a new song with Spotify data
        new_song = Song(track_name=track_name, performer=performer, album=album, rating=rating, username=username)
        db.session.add(new_song)
    
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
                rating = int(row['rating'])
                
                # Validate rating range and that other fields are strings
                if (not isinstance(track_name, str) or 
                    not isinstance(performer, str) or 
                    not isinstance(album, str) or 
                    rating < 1 or rating > 5):
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
                rating = int(item['rating'])

                # Validate rating range and that other fields are strings
                if (not isinstance(track_name, str) or 
                    not isinstance(performer, str) or 
                    not isinstance(album, str) or 
                    rating < 1 or rating > 5):
                    raise ValueError
                
                add_or_update_song(track_name, performer, album, rating, username)

            except (KeyError, ValueError):  
                invalid_items += 1
                continue  # skips the current item and moves to the next

        db.session.commit()

        # Flash a message if some items were invalid
        if invalid_items > 0:
            flash('Some imports did not meet the required format', 'warning')


@app.route('/upload_songs', methods=['POST'])
def upload_songs():
    if 'username' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('songs'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('songs'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        extension = filename.rsplit('.', 1)[1].lower()
        
        if extension == "csv":
            add_songs_from_csv(file_path, session['username'])
        elif extension == "json":
            add_songs_from_json(file_path, session['username'])

        flash('Songs have been uploaded successfully!', 'success')
    else:
        flash('Unsupported file type', 'danger')

    return redirect(url_for('songs'))

@app.route('/songs/<int:id>/update', methods=['POST'])
def update_song_rating(id):
    song = Song.query.get(id)
    if song and "new_rating" in request.form:
        new_rating = request.form['new_rating']
        song.update_rating(new_rating)
        return redirect(url_for('songs'))
    else:
        return "Error updating song rating", 400

@app.route('/songs/<int:id>/delete', methods=['POST'])
def delete_song(id):
    song = Song.query.get(id)
    if song:
        db.session.delete(song)
        db.session.commit()
        return redirect(url_for('songs'))
    return "Error deleting song", 404

@app.route('/export_songs', methods=['GET'])
def export_songs():
    # Fetching songs specific to the logged-in user
    songs = Song.query.filter_by(username=session['username']).all()

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

    return Response(stream_with_context(generate()), headers=headers)


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

# This section will create all tables in the database if they don't exist.
with app.app_context():
    db.create_all()