import json
import urllib.request

import acoustid
from config import API_KEY
from dataclasses import dataclass

from tkinter import Tk
from tkinter.filedialog import askopenfilename



@dataclass
class SongMetadata:
    score:        float
    recording_id: str
    title:        str
    artist:       str

    def __str__(self):
        return f'''
Score:        {self.score}
Recording ID: {self.recording_id}
Title:        {self.title}
Artist:       {self.artist}''';



def deep_search_musicbrainz(recording_id: str) -> tuple | None:
    '''
    Queries the MusicBrainz directly using the recording ID to fetch missing metadata.
    
    Parameters
    ----------
    recording_id : str
        The MusicBrainz recording ID for which to fetch metadata.
    
    Returns
    -------
    tuple | None
        A tuple containing the title and artist(s) in the format (title, artist),
        or None if the request fails or no data is found.
    '''

    recognition_result = None
    
    url     = f'https://musicbrainz.org/ws/2/recording/{recording_id}?inc=artists&fmt=json'
    headers = { 'User-Agent': 'MusicAutomata/1.0' }
    
    try:
        req = urllib.request.Request(url, headers = headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
            # Extract title
            title = data.get('title', None)
            
            # Extract artists
            artist_credits = data.get('artist-credit', [])
            artists        = [credit.get('name', '') for credit in artist_credits if 'name' in credit]
            artist_str     = ', '.join(artists) if artists else None
            
            recognition_result = (title, artist_str) if title and artist_str else None
            
    except Exception as e:
        raise RuntimeError('Error fetching metadata from MusicBrainz') from e;
    
    return recognition_result;



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

            if (title is None) or (artist is None):
                metadata        = deep_search_musicbrainz(recording_id)
                (title, artist) = metadata if metadata is not None else ('Unknown Title', 'Unknown Artist')

            recognition_result = SongMetadata(score, recording_id, title, artist)
            break;
            
    except Exception as e:
        raise RuntimeError('Error recognizing song') from e;

    return recognition_result;



if __name__ == '__main__':
    # Pick the audio file with GUI
    Tk().withdraw()
    filename = askopenfilename()

    if filename:
        result = recognize_song(filename)
        print(result)
    else:
        print('No file selected.')
