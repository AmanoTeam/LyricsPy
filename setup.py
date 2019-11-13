import setuptools

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name='LyricsPy',
    version='0.1.5',
    packages=["lyricspy"],
    url='https://github.com/amanoteam/LyricsPy',
    author='AmanoTeam',
    install_requires=['requests', 'bs4', 'google', 'markdownify'],
    author_email='contact@amanoteam.com',
    description='search lyrics on letras.mus.br',
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
