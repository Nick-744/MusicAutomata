import os
import yt_dlp
from typing import Optional
from config import DEFAULT_DOWNLOAD_DIR



def download_song(url: str, output_dir: str = DEFAULT_DOWNLOAD_DIR) -> Optional[str]:
    '''
    Downloads audio from a given URL and converts it to MP3.

    Parameters
    ----------
    url        : str
        The URL of the song to download.
    output_dir : str
        The directory where the downloaded file should be saved.

    Returns
    -------
    str | None
        The path to the downloaded MP3 file, or None if the download fails.
    '''

    os.makedirs(output_dir, exist_ok = True)

    # yt-dlp options for the download
    options = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key':              'FFmpegExtractAudio',
            'preferredcodec':   'mp3',
            'preferredquality': '320',
        }],
        'outtmpl':    f'{output_dir}/%(title)s.%(ext)s',
        'quiet':      False,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            # Extract info and download
            info_dict = ydl.extract_info(url, download = True)
            
            # Get the generated filename
            original_filename = ydl.prepare_filename(info_dict)
            
            # Convert the filename to .mp3
            (root, _)       = os.path.splitext(original_filename)
            downloaded_file = f'{root}.mp3'
            
            return downloaded_file;

    except Exception as e:
        print(f'-> Error during download: {e}')

        return None;



if __name__ == '__main__':
    target_url = input('Enter the URL: ').strip()
    
    if target_url:
        result_path = download_song(target_url)
        if result_path:
            print(f'-> Download complete: {result_path}')
    else:
        print('-> No URL provided.')
