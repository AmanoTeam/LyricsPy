<h1 align="center">
  <img src="https://github.com/edubr029/piics/blob/master/i/011.png?raw=true" alt="LyricsPy" height="250px">
</h1>

<h1 align="center">LyricsPy</h1>

<h3 align="center">A library to search for music lyrics.</h3>

## Installation

LyricsPy can be installed using `pip` from PyPI or from GitHub.

### via PyPI

```bash
pip install -U lyricspy
```

#### via GitHub using pip+git

```bash
pip install -U git+https://github.com/AmanoTeam/LyricsPy
```

## Usage

Using LyricsPy is easy, but let's see some examples:

### Musixmatch example

```python
from lyricspy import Musixmatch
import json

def search_lyrics_and_translation_musixmatch(query, lang="pt", limit=1):
  # Initializes the Musixmatch class
  musixmatch = Musixmatch()
  # Note: after the 2.2.0 update the token is optional

  # Performs an automatic search to obtain the lyrics and their translations
  search_results = musixmatch.auto(query, lang, limit)

  # Saves the results in a JSON file for viewing
  with open("musixmatch_results.json", "w") as f:
    json.dump(search_results, f)

# Example of use
search_lyrics_and_translation_musixmatch("Hello")
```

### Lyrics example

```python
from lyricspy import Lyrics

def search_lyrics_and_translation(query):
  # Initializes the Lyrics class
  lyrics = Lyrics()

  # Performs the initial search to obtain the links to the lyrics
  search_results = lyrics.search(query)

  # Iterates through the search results
  for result in search_results:
    # Extracts the link to the lyrics
    lyrics_link = result["link"]

    # Performs the search for the lyrics on the page of the obtained link
    lyrics_details = lyrics.lyric(result)

    # Prints the title of the song, the lyrics, and the translation (if available)
    print(f"Title: {lyrics_details['music']}")
    print(f"Lyrics: \n{lyrics_details['lyric']}\n")
    if lyrics_details['translation']:
      print(f"Translation: \n{lyrics_details['translation']}\n")

# Example of use
search_lyrics_and_translation("Hello")
```