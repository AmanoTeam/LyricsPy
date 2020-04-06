import setuptools

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name='LyricsPy',
    version='1.0.9',
    packages=["lyricspy"],
    url='https://github.com/amanoteam/LyricsPy',
    author='AmanoTeam',
    install_requires=['urllib3', 'bs4'],
    author_email='contact@amanoteam.com',
    description='search lyrics on musixmatch.com',
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
