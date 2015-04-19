from setuptools import setup


SETUP = {
    'name': 'hollande',
    # TODO: Get version from code
    'version': '0.1',
    'packages': ['hollande'],
    'install_requires': [
        'github3.py==0.9.4',
        'pep8>=1.5.0',
    ],
    'setup_requires': [
        'nose>=1.0',
        'mock>=1.0.0',
    ],
    'author': 'Bobby R. Ward',
    'author_email': 'bobbyrward@gmail.com',
    'description': '',
    'license': 'BSD',
    'keyworks': '',
    'url': '',
    'entry_points': {
        'console_scripts': {
            'hollande = hollande.application:main',
        }
    },
}


setup(**SETUP)
