import io
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from utils.song_downloader import download_song
from utils.song_recognizer import recognize_song, SongMetadata
from utils.audio_file_tagger import apply_metadata_and_rename



def choose_metadata(metadata_results: list[SongMetadata]) -> SongMetadata | None:
    ''' Launches a GUI window to allow the user to select the correct metadata.
    Returns the selected SongMetadata object or None if the user cancels the selection. '''

    selected_meta   = None
    cover_photo_ref = None

    root = tk.Tk()
    root.title('MusicAutomata - Select Metadata')
    root.geometry('1300x650')
    root.protocol('WM_DELETE_WINDOW', root.quit)

    # ---< Layout - Left/Right panes >--- #
    main_pane = tk.PanedWindow(root, orient = tk.HORIZONTAL, sashwidth = 6)
    main_pane.pack(fill = tk.BOTH, expand = True, padx = 10, pady = 10)



    # ---< Left: results list >--- #
    list_frame = tk.Frame(main_pane)
    main_pane.add(list_frame, minsize = 420)

    columns = [
        ('Score', 60, 'center'), ('Title', 200, 'w'), ('Artist', 160, 'w'), ('Album', 160, 'w'), ('Year', 60, 'center')
    ]

    tree = ttk.Treeview(list_frame, columns = [col[0] for col in columns], show = 'headings', selectmode = 'browse')

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

    tree.pack(fill = tk.BOTH, expand = True)



    # ---< Right: preview panel >--- #
    preview_frame = tk.Frame(main_pane)
    main_pane.add(preview_frame, minsize = 420)

    top_preview = tk.Frame(preview_frame)
    top_preview.pack(fill = tk.X, pady = (0, 10))

    cover_label = tk.Label(
        top_preview, text = 'No Cover Art', width = 25, height = 12, relief = tk.SUNKEN, bg = '#ddd'
    )
    cover_label.pack(side = tk.LEFT, padx = (0, 10))

    info_frame = tk.Frame(top_preview)
    info_frame.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)

    field_labels = {}
    fields = ['Title', 'Artist', 'Album', 'Album Artist', 'Year', 'Genres']
    for field in fields:
        row = tk.Frame(info_frame)
        row.pack(fill = tk.X, anchor = 'w', pady = 1)

        tk.Label(row, text = f'{field}:', font = ('Segoe UI', 9, 'bold'), width = 13, anchor = 'w').pack(side = tk.LEFT)

        value_lbl = tk.Label(row, text = '-', anchor = 'w', wraplength = 260, justify = tk.LEFT)
        value_lbl.pack(side = tk.LEFT, fill = tk.X, expand = True)

        field_labels[field] = value_lbl

    tk.Label(preview_frame, text = 'Lyrics:', font = ('Segoe UI', 9, 'bold'), anchor = 'w').pack(fill = tk.X)

    lyrics_frame = tk.Frame(preview_frame)
    lyrics_frame.pack(fill = tk.BOTH, expand = True)

    lyrics_scroll = tk.Scrollbar(lyrics_frame)
    lyrics_scroll.pack(side = tk.RIGHT, fill = tk.Y)

    lyrics_text = tk.Text(
        lyrics_frame, wrap = tk.WORD, height = 12, yscrollcommand = lyrics_scroll.set, state = tk.DISABLED
    )
    lyrics_text.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
    lyrics_scroll.config(command = lyrics_text.yview)

    def update_preview(index: int):
        ''' Refreshes the preview panel for the given candidate index. '''

        nonlocal cover_photo_ref

        meta = metadata_results[index]

        field_labels['Title'].config(       text = meta.title        or 'N/A')
        field_labels['Artist'].config(      text = meta.artist       or 'N/A')
        field_labels['Album'].config(       text = meta.album        or 'N/A')
        field_labels['Album Artist'].config(text = meta.album_artist or 'N/A')
        field_labels['Year'].config(        text = meta.year         or 'N/A')
        field_labels['Genres'].config(      text = meta.genres       or 'N/A')

        # Update the cover art preview
        if meta.cover_art:
            try:
                image = Image.open(io.BytesIO(meta.cover_art))
                image.thumbnail((200, 200))
                cover_photo_ref = ImageTk.PhotoImage(image)
                cover_label.config(image = cover_photo_ref, text = '', width = 200, height = 200)
            except Exception:
                cover_photo_ref = None
                cover_label.config(image = '', text = 'Cover Art\n(preview failed)', width = 25, height = 12)
        else:
            cover_photo_ref = None
            cover_label.config(image = '', text = 'No Cover Art', width = 25, height = 12)

        # Update the lyrics preview
        lyrics_text.config(state = tk.NORMAL)
        lyrics_text.delete('1.0', tk.END)
        lyrics_text.insert('1.0', meta.lyrics if meta.lyrics else 'No lyrics found.')
        lyrics_text.config(state = tk.DISABLED)

        return;

    def on_tree_select():
        if selected := tree.selection():
            update_preview(tree.index(selected[0]))

        return;

    def on_select():
        nonlocal selected_meta

        if selected := tree.selection():
            selected_meta = metadata_results[tree.index(selected[0])]

            root.quit();

        return;

    tree.bind('<<TreeviewSelect>>', on_tree_select)
    tree.bind('<Double-1>', on_select)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill = tk.X, padx = 10, pady = (0, 10))

    tk.Button(btn_frame, text = 'Cancel', command = root.quit, width = 15).pack(side = tk.RIGHT, padx = 5)
    tk.Button(btn_frame, text = 'Select', command = on_select, width = 15).pack(side = tk.RIGHT, padx = 5)

    # Pre-select and preview the first result
    if metadata_results:
        first_item = tree.get_children()[0]
        tree.selection_set(first_item)
        tree.focus(first_item)
        update_preview(0)

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
