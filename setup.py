import setuptools

setuptools.setup(
    name='LyricsPy',
    version='0.1.1',
    packages=setuptools.find_packages(),
    url='https://github.com/amanoteam/LyricsPy',
    author='AmanoTeam',
    install_requires=['requests','bs4','google','markdownify'],
    author_email='contact@amanoteam.ml',
    description='search lyrics on letras.mus',
    long_description='No description for now',
    long_description_content_type="text/markdown"
)
