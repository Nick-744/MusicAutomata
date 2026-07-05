import acoustid
from config import API_KEY

from tkinter import Tk
from tkinter.filedialog import askopenfilename



def recognize_song(filename: str) -> tuple | None:
    '''
    Recognizes a song from a given audio file using the AcoustID API.

    Parameters
    ----------
    filename : str
        The path to the audio file to be recognized.

    Returns
    -------
    tuple | None
        A tuple containing the recognition result in the format (score, recording_id, title, artist)
        if a match is found, or None if no match is found or an error occurs during recognition.
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
            recognition_result = (score, recording_id, title, artist)
            break;
    except Exception as e:
        raise RuntimeError('Error recognizing song') from e;

    return recognition_result;



if __name__ == '__main__':
    # Pick the audio file with GUI
    Tk().withdraw()
    filename = askopenfilename()

    print(recognize_song(filename))
