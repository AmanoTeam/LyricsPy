<h6 align="center">
  <img src="https://piics.ml/i/011.png" alt="LyricsPy" height="250px">
  <h5 align="center">A library to search for music lyrics.</h5>
</h6>

## Installation

LyricsPy can be installed using pip from PyPI or from GitHub

#### via PyPI using pip

```bash
pip install -U lyricspy
```

#### via GitHub using pip+git

```bash
pip install -U git+https://github.com/AmanoTeam/LyricsPy
```

## Usage

To use LyricsPy is easy, but let's see some examples:

### Musixmatch example

```python
from lyricspy import Musixmatch
from json import dump

search = Musixmatch("Musixmatch key").auto("Hello",lang="pt" , limit=1)

with open("lyrics.json", "w") as f:
  dump(search, f)
```
