# MusicAutomata

MusicAutomata is an automated music downloader and tagger. It downloads audio from a URL, generates an acoustic fingerprint to identify the track, pulls metadata, album art, and lyrics from online databases, and gives you an interactive GUI to verify and save the tagged file.

---

## Features

* **High-Quality Downloads**: Uses `yt-dlp` to grab audio and converts it to a 320kbps MP3 via FFmpeg.
* **Acoustic Fingerprinting**: Leverages the AcoustID API to accurately identify songs regardless of the source file name.
* **Deep Metadata Enrichment**: Automatically queries MusicBrainz for release information, release years, and genres.
* **Artwork & Lyrics Fetching**: Pulls front covers from the Cover Art Archive and plain-text lyrics from LRCLIB.
* **Interactive Metadata Selector**: A Tkinter GUI allows you to preview matches, inspect cover art, clear/paste lyrics, and select the best metadata candidate.
* **Automated Organization**: Automatically embeds ID3 tags (including APIC for covers and USLT for lyrics) and renames files cleanly to `Title - Artist.mp3`.

---

## Prerequisites

Before running the application, make sure you have Python installed along with the following tools configured in your system's PATH:

* **FFmpeg** — required by `yt-dlp` for audio conversion.
* **fpcalc** (Chromaprint) — required by `acoustid` to generate acoustic fingerprints. Download it from [acoustid.org/chromaprint](https://acoustid.org/chromaprint).

### Install Dependencies

Install the required Python libraries using pip:

```bash
pip install mutagen yt-dlp pyacoustid Pillow

```

---

## Setup & Configuration

1. **AcoustID API Key**: You need a free API key from [AcoustID](https://acoustid.org/).
2. **Configuration File**: Create a file named `api_key.txt` as per instructed ([`SourceCode/utils/config.py`](./SourceCode/utils/config.py)).
3. **Default Download Directory**: By default, songs are saved directly to your system's default `Music` folder (`~/Music`).

---

## Usage

Run the main application script:

```bash
python main.py

```

### Workflow

1. **Provide URL**: The terminal will prompt you to enter a URL.
2. **Download & Scan**: The tool downloads the track and analyzes its acoustic fingerprint.
3. **Review Candidates**: The interactive GUI will pop up showing the closest metadata matches.
4. **Done!** The file is tagged, renamed, and organized automatically.
