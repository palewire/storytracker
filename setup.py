import sys
from setuptools import setup

install_requires = [
    'python-dateutil>=2.2',
    'requests>=2.3.0',
    'htmlmin==0.1.5',
    'six>=1.7.2',
    'pytz>=2014.4',
    'beautifulsoup4>=4.3.2',
    'storysniffer==0.0.3',
    'selenium>=2.42.1',
    'Pillow>=2.5.3',
]

if sys.version_info < (3,):
    install_requires.append('unicodecsv>=0.9.4')

setup(
    name='storytracker',
    version='0.0.9',
    description='Tools for tracking stories for news homepages',
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='https://github.com/pastpages/storytracker',
    license='MIT',
    packages=('storytracker',),
    scripts=(
        'bin/storytracker-archive',
        'bin/storytracker-get',
        'bin/storytracker-links2csv',
    ),
    install_requires=install_requires,
)
