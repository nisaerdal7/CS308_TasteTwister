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
    token = db.Column(db.String(255), nullable=False)  # Assuming token should be non-nullable
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
        return jsonify({'message': 'User is already logged in'})
    return jsonify({'message': 'Welcome to TasteTwister'})


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Generate a unique token for the new user
        unique_token = secrets.token_hex(16)
        
        # Include the token when creating the new User object
        new_user = User(username=username, password=hashed_pw, token=unique_token)
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Registration successful!', 'token': unique_token})
    
    return jsonify({'message': 'Use POST request to register'})


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            session['username'] = user.username
            # Return username and token in the response
            return jsonify({
                'message': 'Login successful!',
                'username': user.username,
                'token': user.token
            })
        else:
            return jsonify({'message': 'Login failed! Check your credentials.'})
    
    return jsonify({'message': 'Use POST request to log in'})



@app.route('/logout')
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'})


@app.route('/songs', methods=['GET', 'POST'])
def songs():
    if 'username' not in session:
        return jsonify({'message': 'Please log in first.'}), 401

    if request.method == 'POST':
        data = request.get_json()
        track_name = data['track_name']
        performer = data['performer']
        album = data['album']
        rating = data['rating']

        # Use the helper function to add or update the song
        add_or_update_song(track_name, performer, album, rating, session['username'])
        return jsonify({'message': 'Song added or updated!'}), 201

    songs = Song.query.filter_by(username=session['username']).all()
    return jsonify([
        {
            "id": song.id,
            "track_name": song.track_name,
            "performer": song.performer,
            "album": song.album,
            "rating": song.rating
        } for song in songs
    ])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_or_update_song(track_name, performer, album, rating, username):
    # Check if the song already exists for the user
    existing_song = Song.query.filter_by(track_name=track_name, performer=performer, album=album, username=username).first()
    if existing_song:
        existing_song.update_rating(rating)
    else:
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
        return jsonify({'message': 'Please log in first.'}), 401

    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        extension = filename.rsplit('.', 1)[1].lower()

        if extension == "csv":
            add_songs_from_csv(file_path, session['username'])
        elif extension == "json":
            add_songs_from_json(file_path, session['username'])

        return jsonify({'message': 'Songs uploaded successfully!'})
    
    return jsonify({'message': 'Unsupported file type'}), 400


@app.route('/songs/<int:id>/update', methods=['POST'])
def update_song_rating(id):
    song = Song.query.get(id)
    if song and "new_rating" in request.form:
        new_rating = request.form['new_rating']
        song.update_rating(new_rating)
        return jsonify({'message': 'Song rating updated successfully!'})
    return jsonify({'message': 'Error updating song rating'}), 400

@app.route('/songs/<int:id>/delete', methods=['POST'])
def delete_song(id):
    song = Song.query.get(id)
    if song:
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted successfully!'})
    return jsonify({'message': 'Error deleting song'}), 404

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