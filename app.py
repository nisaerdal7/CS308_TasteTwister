from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Flask configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:backend777@35.240.109.106/tastetwister'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence the deprecation warning
app.config['SECRET_KEY'] = 'your_secret_key_here'  # For session management, replace with a strong key

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
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
        if user and user.password == password:
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
            new_song = Song(
                track_name=data['track_name'],
                performer=data['performer'],
                album=data['album'],
                rating=data['rating'],
                username=session['username']
            )
        else:
            track_name = request.form['track_name']
            performer = request.form['performer']
            album = request.form['album']
            rating = request.form['rating']
            new_song = Song(track_name=track_name, performer=performer, album=album, rating=rating, username=session['username'])

        db.session.add(new_song)
        db.session.commit()

        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({"message": "Song added!"}), 201
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



if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()

