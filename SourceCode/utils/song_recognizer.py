import json
import urllib.parse
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
    title:        str | None = None
    artist:       str | None = None

    album:        str | None = None
    album_artist: str | None = None
    year:         str | None = None
    genres:       str | None = None

    cover_art:  bytes | None = None
    cover_mime: str   | None = None

    lyrics: str | None = None

    def __str__(self):
        return f'''
Title:        {self.title}
Artist:       {self.artist}
Album:        {self.album if self.album else 'N/A'}
Album Artist: {self.album_artist if self.album_artist else 'N/A'}
Year:         {self.year if self.year else 'N/A'}
Genres:       {self.genres if self.genres else 'N/A'}
Cover Art:    {'Yes' if self.cover_art else 'N/A'}
Lyrics:       {'Yes' if self.lyrics else 'N/A'}
-------------
Score:        {self.score}
Recording ID: {self.recording_id}''';



def fetch_cover_art(release_id: str) -> tuple[bytes, str] | None:
    '''
    Fetches the front cover art image for a given MusicBrainz release from the Cover Art Archive.

    Parameters
    ----------
    release_id : str
        The MusicBrainz release ID for which to fetch cover art.

    Returns
    -------
    tuple[bytes, str] | None
        A tuple of (image_bytes, mime_type) if cover art was found,
        or None if no cover art is available or an error occurs.
    '''

    url     = f'https://coverartarchive.org/release/{release_id}/front'
    headers = { 'User-Agent': 'MusicAutomata/1.0' }

    try:
        req = urllib.request.Request(url, headers = headers)
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
            mime_type  = response.headers.get('Content-Type', 'image/jpeg')

            return (image_data, mime_type);

    except Exception as e:
        print(f'-> Fetching cover art failed: {e}')

        return None;



def fetch_lyrics(artist: str, title: str) -> str | None:
    '''
    Fetches plain-text lyrics for a given artist/title from the LRCLIB API.

    Parameters
    ----------
    artist : str
        The track's artist name.
    title  : str
        The track's title.

    Returns
    -------
    str | None
        The lyrics text if found, or None if unavailable or an error occurs.
    '''

    if not artist or not title:
        return None;

    query   = urllib.parse.urlencode({
        'artist_name': artist,
        'track_name':  title
    })
    url     = f'https://lrclib.net/api/search?{query}'
    headers = { 'User-Agent': 'MusicAutomata/1.0' }

    try:
        req = urllib.request.Request(url, headers = headers)
        with urllib.request.urlopen(req, timeout = 20) as response:
            data = json.loads(response.read().decode())
            
            # Iterate through the results to find the plain-text lyrics...
            for match in data:
                lyrics = match.get('plainLyrics')
                if lyrics:
                    return lyrics.strip();

    except Exception as e:
        print(f'-> Fetching lyrics failed: {e}')

        return None;

    return None; # No lyrics found...



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
    
    url      = f'https://musicbrainz.org/ws/2/recording/{recording_id}?inc=artists+releases+release-groups+genres&fmt=json'
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
                def score_release(r: dict) -> tuple[int, int]:
                    ''' Scores a release based on its attributes to prioritize the best match.
                    Returns a tuple of (score, -year) for sorting purposes.
                    
                    Not the best solution, but it works for now... '''

                    score = 0

                    # Prioritize official releases
                    if r.get('status') == 'Official':
                        score += 10
                    
                    # Check release group types
                    rg      = r.get('release-group', {})
                    p_type  = rg.get('primary-type')
                    s_types = rg.get('secondary-types', [])
                    
                    # Apply bonuses for certain primary types
                    if p_type == 'Album':
                        score += 10
                    elif p_type in ['EP', 'Single']:
                        score += 5
                    
                    # Apply penalties for certain secondary types
                    if 'Compilation' in s_types:
                        score -= 15
                    if 'Live' in s_types:
                        score -= 10

                    # Apply bonuses for certain countries
                    country = r.get('country', '')
                    if country in ['JP', 'US', 'XW']:
                        score += 2
                    
                    # Extract the year from the date string for sorting
                    date_str = r.get('date', '9999')
                    if len(date_str) >= 4 and date_str[:4].isdigit():
                        year = int(date_str[:4])
                    else:
                        year = 9999
                    
                    # -year -> Hack for sorting in reverse order (older releases first)
                    return (score, -year);

                # Sort releases based on the scoring function!
                releases.sort(key = score_release, reverse = True)
                # Grab the best available release
                best_release = releases[0]
                
                if best_release.get('title'):
                    metadata['album'] = best_release['title']
                
                # Extract the Year from the Date string
                date_str = best_release.get('date', '')
                if date_str:
                    metadata['year'] = date_str[:4]
                
                # Extract Album Artist if it differs from the Track Artist
                album_artist_credits = best_release.get('artist-credit', [])
                album_artists        = [credit.get('name', '') for credit in album_artist_credits if 'name' in credit]
                if album_artists:
                    metadata['album_artist'] = ', '.join(album_artists)
                else:
                    metadata['album_artist'] = metadata.get('artist')

                # Fetch the cover art (thumbnail) using the release ID
                release_id = best_release.get('id')
                if release_id:
                    cover_result = fetch_cover_art(release_id)
                    if cover_result:
                        (cover_data, cover_mime) = cover_result
                        metadata['cover_art']    = cover_data
                        metadata['cover_mime']   = cover_mime
            
    except Exception as e:
        print(f'-> Fetching metadata from MusicBrainz failed: {e}')

        return {}; # If any error occurs, return an empty dictionary!
    
    return metadata;



def recognize_song(filename: str) -> list[SongMetadata]:
    '''
    Recognizes a song from a given audio file using the AcoustID API.

    Parameters
    ----------
    filename : str
        The path to the audio file to be recognized.

    Returns
    -------
    list[SongMetadata]
        A list of SongMetadata objects containing the recognition results.
        If no matches are found or an error occurs, an empty list is returned.
    '''

    recognition_results = []

    try:
        results = acoustid.match(
            apikey = API_KEY,
            path   = filename,
            meta   = 'recordings',

            force_fpcalc = True
        )
        
        for (score, recording_id, title, artist) in results:
            if score < 0.9:
                continue; # Skip low-confidence matches!
            
            deep_data = deep_search_musicbrainz(recording_id)

            final_title  = deep_data.get('title', title)
            final_artist = deep_data.get('artist', artist)
            lyrics       = fetch_lyrics(final_artist, final_title)

            recognition_results.append(SongMetadata(
                score        = score,
                recording_id = recording_id,
                title        = final_title,
                artist       = final_artist,
                album        = deep_data.get('album'),
                album_artist = deep_data.get('album_artist'),
                year         = deep_data.get('year'),
                genres       = deep_data.get('genres'),
                cover_art    = deep_data.get('cover_art'),
                cover_mime   = deep_data.get('cover_mime'),
                lyrics       = lyrics
            ))
            
    except Exception as e:
        raise RuntimeError('Error recognizing song') from e;

    return recognition_results;



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
