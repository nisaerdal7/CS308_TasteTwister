# TasteTwister

Welcome to our Music Recommendation App! This project encompasses a web application and a mobile application for music lovers. The backend is built using Python, Flask, and MySQL, while the frontend uses React, and the mobile app is developed with Flutter.

## Getting Started

To run the front end, ensure you have Node.js and npm installed. Navigate to the frontend directory and run the following commands:

```
npm install
npm start
```
For the backend, you need Python3 installed. Install the required dependencies:

```
pip install Flask Flask-SQLAlchemy Flask-Bcrypt
```
And then run the Flask app:

```
python app.py
```

For the mobile application, make sure you have Flutter and Dart installed, and ensure that an Android device is connected or an Android emulator is open. Navigate to the 'taste_twisters_mobile' directory and execute the following commands:
```
flutter run lib/main_development.dart --flavor development
```
## API Requests
### 1. Home Route (/)
GET Request: Simply accessing the root URL (/) would return the welcome message.

### 2. Register Route (/register)
POST Request:

URL: /register  
Method: POST  
Body:
```
{
 "username": "newuser",
 "password": "password123"
}
```
### 3. Login Route (/login)
POST Request:  

URL: /login  
Method: POST  
Body:
```
{
 "username": "existinguser",
 "password": "password123"
}
```
### 4. Logout Route (/logout)
POST Request:

URL: /logout  
Method: POST  
Headers:
```
{
 "Authorization": "user_token"
}
```
### 5. Songs Route (/songs)
GET Request:

URL: /songs?username=username  
Method: GET  
POST Request:  
 
URL: /songs  
Method: POST  
```
{
 "Authorization": "user_token"
}
Body:
{
 "track_name": "song name",
 "performer": "artist",
 "album": "album name",
 "rating": 5
}
```
### 6. Upload Songs Route (/upload_songs)
POST Request (for file upload):

URL: /upload_songs  
Method: POST  
Headers:  
```
{
 "Authorization": "user_token"
}
```
Body: FormData with the song file
### 7. Update Song Rating Route (/songs/<int:id>/update)
POST Request:  

URL: /songs/1/update   
Method: POST  
Headers:
```
{
 "Authorization": "user_token"
}
Form Data:
{
 "new_rating": 4
}
```
### 8. Delete Song Route (/songs/<int:id>/delete)
POST Request:  

URL: /songs/1/delete  
Method: POST  
Headers:
```
{
 "Authorization": "user_token"
}
```
### 9. Export Songs Route (/export_songs)
GET Request:

URL: /export_songs  
Method: GET  
Headers:  
```
{
 "Authorization": "user_token"
}
```
## ER Diagram
<img width="487" alt="image" src="https://github.com/nisaerdal7/CS308_TasteTwister/assets/76566903/18465dae-d2d9-4f03-b254-5a8d3b0e38fa">


## MVP Features
Our Minimum Viable Product (MVP) includes the following features:

#### Data Format:

Basic song information includes track name, performer(s), album, and user rating.  
Handle multiple performers and versions of the same song.  
#### Data Collection:

Manual user input via web/mobile application.  
Batch input via file upload.  
Import data from a self-hosted or cloud database service.  
Rate non-rated songs/albums/performers.  
Remove a song/album/performer from the system.  
#### Analysis of Musical Choices:

Display statistical information about user likings.   
Create tables and charts based on user preferences.   
Allow user customization of analysis mediums.  
#### Recommendations:

Provide music recommendations based on user ratings.  
Make recommendations based on temporal properties and genres.  
Recommend based on friendship activity.  
#### Social Features:

User authentication with password.  
Friend management with customizable activity inclusion.  
Share analysis results on social media.  
Export user ratings with filtering options.  

## Additional Features 
In addition to the MVP, specific features are being implemented:  

Added a feature to add all songs from a Spotify playlist using the playlist URL.  
Performed cross-checks using the Spotify API.  
Database hosted on Google Cloud.  

##### Thank you for checking out TasteTwister!

Developed by Betül Koç, Yunus Topçu, Sude Alan, Nisa Erdal, Burak Ersöz and Emir Aikan

