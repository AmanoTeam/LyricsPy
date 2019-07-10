import setuptools

with open("README.md") as f:
    long_desc = f.read()

setuptools.setup(
    name='LyricsPy',
    version='0.1.3-2',
    packages=setuptools.find_packages(),
    url='https://github.com/amanoteam/LyricsPy',
    author='AmanoTeam',
    install_requires=['requests', 'bs4', 'duckpy', 'markdownify'],
    author_email='contact@amanoteam.ml',
    description='search lyrics on letras.mus',
    long_description=long_desc,
    long_description_content_type="text/markdown"
)
