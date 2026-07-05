from pathlib import Path

# ---< API Key >--- #
# Put the API key in a file called 'api_key.txt' in the same directory as this file.
API_KEY = Path(__file__).resolve().parent / 'api_key.txt'
API_KEY = API_KEY.read_text(encoding = 'utf-8').strip()
