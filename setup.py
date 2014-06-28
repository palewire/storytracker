from distutils.core import setup

setup(
    name='storytracker',
    version='0.0.1',
    description='Tools for tracking stories for news homepages',
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='https://github.com/pastpages/storytracker',
    license='MIT',
    packages=('storytracker',),
    scripts=(
        'bin/storytracker-archive',
        'bin/storytracker-get',
    ),
    install_requires=(
        'beautifulsoup4==4.3.2',
        'python-dateutil==2.2',
        'requests==2.3.0',
        'htmlmin==0.1.5',
        'six==1.7.2',
    ),
)
