import setuptools

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name='LyricsPy',
    version='1.0.8',
    packages=["lyricspy"],
    url='https://github.com/amanoteam/LyricsPy',
    author='AmanoTeam',
    install_requires=['selenium-requests-html', 'requests_html', 'selenium', 'bs4'],
    author_email='contact@amanoteam.com',
    description='search lyrics on musixmatch.com',
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
