import spotipy
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
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyOAuth, Spotify
import spotipy.util as util
import re


# Spotify API authentication

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

playlist_id = 'https://open.spotify.com/playlist/301LWJNRPghxx6YaslxOyX?si=151587a1afab45ad'
results = sp.playlist(playlist_id)

def extract_music_info_from_results(results):
    songs = []
    for item in results['tracks']['items']:
        track = item['track']
        song_name = track['name']
        album_name = track['album']['name']
        artists = [artist['name'] for artist in track['artists']]
        songs.append({
            'track_name': song_name,
            'album': album_name,
            'performer': artists
        })
    return json.dumps({'songs': songs}, indent=4)



# Extract music information
extracted_songs = extract_music_info_from_results(results)

print(extracted_songs)