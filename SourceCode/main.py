import sys
from utils.song_downloader import download_song
from utils.song_recognizer import recognize_song
from utils.audio_file_tagger import apply_metadata_and_rename



def main():
    print('\n>=== MusicAutomata ===<\n')
    
    # Get the URL
    target_url = input('Enter the URL: ').strip()
    if not target_url:
        print('\n-> No URL provided. Exiting...')

        sys.exit(1);

    # Download the audio
    downloaded_file = download_song(target_url)
    if not downloaded_file:
        print('\n-> Process aborted due to download failure. Exiting...')

        sys.exit(1);

    # Recognize the audio
    metadata = recognize_song(downloaded_file)
    if not metadata:
        print('\n-> Could not recognize the song. The file was saved without tags. Exiting...')

        sys.exit(1);
    
    print(f'{metadata}\n')

    # Apply tags and rename
    final_filepath = apply_metadata_and_rename(downloaded_file, metadata)
    if final_filepath:
        print(f'\n-> Process complete! Final file: {final_filepath}')
    else:
        print('\n-> Process failed during tagging/renaming. Exiting...')

        sys.exit(1);

    return;



if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print('\n-> Process interrupted by user. Exiting...')

            sys.exit(0);
