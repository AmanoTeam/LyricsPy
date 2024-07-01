import setuptools

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name='LyricsPy',
    version='2.2.0',
    packages=["lyricspy", "lyricspy.aio"],
    url='https://github.com/amanoteam/LyricsPy',
    author='Amano Team',
    install_requires=['httpx'],
    author_email='contact@amanoteam.com',
    description='search lyrics on musixmatch.com',
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
