<h6 align="center">
  <img src="https://raw.githubusercontent.com/edubr029/piics/master/i/011.png" alt="LyricsPy" height="250px">
  <h5 align="center">A library for searching music lyrics.</h5>
</h6>

## Installation

You can install LyricsPy using pip either from PyPI or GitHub.

### Install via PyPI

```bash
pip install -U lyricspy
```

### Install via GitHub

```bash
pip install -U git+https://github.com/AmanoTeam/LyricsPy
```

## Usage

Using LyricsPy is straightforward. Here are some examples:

### Example with Musixmatch

```python
import asyncio
from pprint import pprint

from lyricspy import Musixmatch

async def main():
    musixmatch = Musixmatch([
        "Musixmatch API key 1",
        "Musixmatch API key 2",
    ])
    search = await musixmatch.auto("Hello", lang="pt", limit=1)
    parsed_output = musixmatch.parse(search[0])

    pprint(parsed_output, indent=4)

asyncio.run(main())
```
