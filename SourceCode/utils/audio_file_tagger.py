import mutagen
from pathlib import Path
from .song_recognizer import SongMetadata
from mutagen.id3 import ID3, APIC, ID3NoHeaderError



def embed_cover_art(filename: str, cover_art: bytes, cover_mime: str | None = None) -> bool:
    '''
    Embeds cover art (the thumbnail) into an audio file's tags.

    Parameters
    ----------
    filename   : str
        The path to the audio file to embed the cover art into.
    cover_art  : bytes
        The raw image bytes to embed.
    cover_mime : str | None
        The MIME type of the image (defaults to 'image/jpeg').

    Returns
    -------
    bool
        True if the cover art was embedded successfully, False otherwise.
    '''

    mime_type = cover_mime or 'image/jpeg'

    try:
        try:
            tags = ID3(filename)
        except ID3NoHeaderError:
            tags = ID3()

        tags.delall('APIC')
        tags.add(APIC(
            encoding = 3, # UTF-8
            mime     = mime_type,
            type     = 3, # Front cover
            desc     = 'Cover',
            data     = cover_art
        ))
        tags.save(filename)

        print('-> Cover art embedded successfully.')

        return True;

    except Exception as e:
        print(f'-> Error embedding cover art: {e}')

        return False;



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

        # Embed the cover art (thumbnail), if one was found...
        if metadata.cover_art:
            embed_cover_art(filename, metadata.cover_art, metadata.cover_mime)
        
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
