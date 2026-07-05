import mutagen
from pathlib import Path
from .song_recognizer import SongMetadata



def apply_metadata_and_rename(filename: str, metadata: SongMetadata) -> str | None:
    '''
    Apply metadata to an audio file and rename it based on the metadata.

    Parameters
    ----------
    filename : str
        The path to the audio file to be tagged and renamed.
    metadata : SongMetadata
        An instance of the SongMetadata class containing the metadata to be applied.

    Returns
    -------
    str | None
        The new filename if the operation was successful, or None if there was an error.
    '''

    try:
        # Write the metadata to the audio file's tags
        audio = mutagen.File(filename, easy = True)
        
        if audio is None:
            print('-> Could not open audio file for tagging.')

            return None;
        
        if audio.tags is None:
            audio.add_tags()

        if metadata.title:        audio['title']       = metadata.title
        if metadata.artist:       audio['artist']      = metadata.artist
        if metadata.album:        audio['album']       = metadata.album
        if metadata.album_artist: audio['albumartist'] = metadata.album_artist
        if metadata.year:         audio['date']        = metadata.year
        if metadata.genres:       audio['genre']       = metadata.genres
        
        audio.save()
        print('-> Metadata written successfully.')
        
    except Exception as e:
        print(f'-> Error writing metadata: {e}')

        return None;

    try:
        # Rename the audio file
        file_path = Path(filename)
        extension = file_path.suffix
        
        new_filename = f'{metadata.title} - {metadata.artist}{extension}'
        new_filepath = file_path.parent / new_filename
        
        if new_filepath.exists() and new_filepath != file_path:
            print(f"-> A file named \'{new_filename}\' already exists.")
            file_path.unlink() # Delete the original file to avoid duplicates!

            return str(new_filepath);

        file_path.rename(new_filepath)
        print(f'-> File {new_filename} has been named successfully.')
        
        return str(new_filepath);
        
    except Exception as e:
        print(f'-> Error naming file: {e}')

        return str(file_path);
