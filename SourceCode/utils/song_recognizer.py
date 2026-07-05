import json
import urllib.request

import acoustid
from .config import API_KEY
from dataclasses import dataclass

from tkinter import Tk
from tkinter.filedialog import askopenfilename



@dataclass
class SongMetadata:
    score:        float
    recording_id: str
    title:        str
    artist:       str
    album:        str | None = None
    album_artist: str | None = None
    year:         str | None = None
    genres:       str | None = None

    def __str__(self):
        return f'''
Title:        {self.title}
Artist:       {self.artist}
Album:        {self.album if self.album else 'N/A'}
Album Artist: {self.album_artist if self.album_artist else 'N/A'}
Year:         {self.year if self.year else 'N/A'}
Genres:       {self.genres if self.genres else 'N/A'}
-------------
Score:        {self.score}
Recording ID: {self.recording_id}''';



def deep_search_musicbrainz(recording_id: str) -> dict:
    '''
    Queries the MusicBrainz directly using the recording ID to fetch missing metadata.
    
    Parameters
    ----------
    recording_id : str
        The MusicBrainz recording ID for which to fetch metadata.

    Returns
    -------
    dict
        A dictionary containing the fetched metadata if available,
        or an empty dictionary if no metadata is found or an error occurs.
    '''
    
    url      = f'https://musicbrainz.org/ws/2/recording/{recording_id}?inc=artists+releases+genres&fmt=json'
    headers  = { 'User-Agent': 'MusicAutomata/1.0' }
    metadata = {}
    
    try:
        req = urllib.request.Request(url, headers = headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            # Extract title
            if data.get('title'):
                metadata['title'] = data['title']
            
            # Extract artists
            artist_credits = data.get('artist-credit', [])
            artists        = [credit.get('name', '') for credit in artist_credits if 'name' in credit]
            if artists:
                metadata['artist'] = ', '.join(artists)
            
            # Extract genres
            genre_list = [g.get('name', '').title() for g in data.get('genres', [])]
            if genre_list:
                metadata['genres'] = ', '.join(genre_list)
            
            # Extract album and year from releases
            releases = data.get('releases', [])
            if releases:
                # Grab the 1st available release
                first_release = releases[0]
                
                if first_release.get('title'):
                    metadata['album'] = first_release['title']
                
                # Extract the Year from the Date string
                date_str = first_release.get('date', '')
                if date_str:
                    metadata['year'] = date_str[:4]
                
                # Extract Album Artist if it differs from the Track Artist
                album_artist_credits = first_release.get('artist-credit', [])
                album_artists        = [credit.get('name', '') for credit in album_artist_credits if 'name' in credit]
                if album_artists:
                    metadata['album_artist'] = ', '.join(album_artists) if album_artists else metadata['artist']
            
    except Exception as e:
        print(f'Fetching metadata from MusicBrainz failed: {e}')

        return {}; # If any error occurs, return an empty dictionary!
    
    return metadata;



def recognize_song(filename: str) -> SongMetadata | None:
    '''
    Recognizes a song from a given audio file using the AcoustID API.

    Parameters
    ----------
    filename : str
        The path to the audio file to be recognized.

    Returns
    -------
    SongMetadata | None
        A SongMetadata object containing the recognition result if a match is found,
        or None if no match is found or an error occurs during recognition.
    '''

    recognition_result = None

    try:
        results = acoustid.match(
            apikey = API_KEY,
            path   = filename,
            meta   = 'recordings',

            force_fpcalc = True
        )
        
        for (score, recording_id, title, artist) in results:
            deep_data = deep_search_musicbrainz(recording_id)
            
            recognition_result = SongMetadata(
                score        = score,
                recording_id = recording_id,
                title        = deep_data.get('title', title),
                artist       = deep_data.get('artist', artist),
                album        = deep_data.get('album'),
                album_artist = deep_data.get('album_artist'),
                year         = deep_data.get('year'),
                genres       = deep_data.get('genres')
            )
            
            break; # We only care about the first match!
            
    except Exception as e:
        raise RuntimeError('Error recognizing song') from e;

    return recognition_result;



if __name__ == '__main__':
    # Pick the audio file with GUI
    root = Tk()
    root.withdraw()
    filename = askopenfilename()
    root.destroy()

    if filename:
        result = recognize_song(filename)
        print(result)
    else:
        print('No file selected.')
