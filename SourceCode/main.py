import sys
import tkinter as tk
from tkinter import ttk

from utils.song_downloader import download_song
from utils.song_recognizer import recognize_song, SongMetadata
from utils.audio_file_tagger import apply_metadata_and_rename



def choose_metadata(metadata_results: list[SongMetadata]) -> SongMetadata | None:
    ''' Launches a GUI window to allow the user to select the correct metadata from a list of results.
    Returns the selected SongMetadata object or None if the user cancels the selection. '''

    selected_meta = None

    def on_select():
        nonlocal selected_meta

        if selected := tree.selection():
            selected_meta = metadata_results[tree.index(selected[0])]

            root.quit();

        return;

    root = tk.Tk()
    root.title('MusicAutomata - Select Metadata')
    root.geometry('1000x500')
    root.protocol('WM_DELETE_WINDOW', root.quit)

    columns = [
        ('Score', 60, 'center'), ('Title', 220, 'w'), ('Artist', 180, 'w'), ('Album', 220, 'w'), ('Year', 60, 'center')
    ]
    
    tree = ttk.Treeview(root, columns = [col[0] for col in columns], show = 'headings', selectmode = 'browse')
    
    # Apply headings and column formatting
    for (name, width, anchor) in columns:
        tree.heading(name, text = name)
        tree.column(name, width = width, anchor = anchor)

    # Insert data rows
    for meta in metadata_results:
        score_str = f'{meta.score:.2f}'
        tree.insert('', tk.END, values = (
            score_str, meta.title or 'N/A', meta.artist or 'N/A', meta.album or 'N/A', meta.year or 'N/A'
        ))

    tree.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)
    tree.bind('<Double-1>', on_select)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill = tk.X, padx = 10, pady = 10)

    tk.Button(btn_frame, text = 'Cancel', command = root.quit, width = 15).pack(side = tk.RIGHT, padx = 5)
    tk.Button(btn_frame, text = 'Select', command = on_select, width = 15).pack(side = tk.RIGHT, padx = 5)

    root.mainloop()
    root.destroy()
    
    return selected_meta;



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
    metadata_results = recognize_song(downloaded_file)
    if not metadata_results:
        print('\n-> Could not recognize the song. The file was saved without tags. Exiting...')

        sys.exit(1);
    
    # Launch GUI for user to choose the correct metadata
    selected_metadata = choose_metadata(metadata_results)
    if not selected_metadata:
        print('\n-> No metadata selected (Action cancelled). Exiting...')

        sys.exit(1);
    
    print(f'{selected_metadata}\n')

    # Apply tags and rename
    final_filepath = apply_metadata_and_rename(downloaded_file, selected_metadata)
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
