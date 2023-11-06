'''from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import csv
import json
from werkzeug.utils import secure_filename
from sqlalchemy import MetaData, Table
from flask import Response, stream_with_context
from io import StringIO
from flask_cors import CORS



app = Flask(__name__)
CORS(app) 
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
        # Modify the response to return a JSON message
        return jsonify({'message': 'User is already logged in'})

    return jsonify({'message': 'Welcome to TasteTwister'})

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()  # Assuming the frontend sends JSON data
        username = data.get('username')
        password = data.get('password')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Successful'})

    # Return a JSON response for the GET request
    return jsonify({'message': 'Use POST request to register'})

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()  # Assuming the frontend sends JSON data
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['username'] = user.username
            print("geldim")
            return jsonify({'message': 'Authenticated'})
        else:
            return jsonify({'message': 'Failed'})

    # Return a JSON response for the GET request
    return jsonify({'message': 'Use POST request to log in'})

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
            new_song = Song(
                track_name=data['track_name'],
                performer=data['performer'],
                album=data['album'],
                rating=data['rating'],
                username=session['username']
            )

            db.session.add(new_song)
            db.session.commit()

            return jsonify({"message": "Song added!"}), 201

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

def add_songs_from_csv(file_path, username):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            song = Song(track_name=row['track_name'], performer=row['performer'], album=row['album'], rating=int(row['rating']), username=username)
            db.session.add(song)
        db.session.commit()

def add_songs_from_json(file_path, username):
    with open(file_path) as jsonfile:
        data = json.load(jsonfile)
        for item in data:
            try:
                track_name = item['track_name']
                performer = item['performer']  # this line may raise the KeyError
                album = item['album']
                rating = int(item['rating'])
            except KeyError as e:
                print(f"KeyError: {e} not found in item: {item}")
                continue  # skips the current item and moves to the next

            song = Song(track_name=track_name, performer=performer, album=album, rating=rating, username=username)
            db.session.add(song)
    db.session.commit()

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
    db.create_all()'''