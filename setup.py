from setuptools import setup
import handyhelpers

setup(
    name='django-handyhelpers',
    packages=['djangohelpers'],
    version=handyhelpers.__version__,
    license=handyhelpers.__license__,
    author='David Slusser',
    author_email='dbslusser@gmail.com',
    description='A collection of handy utilities to support django operations',
    long_description='A collection of handy utilities to support django operations',
    url='https://github.com/davidslusser/django-handyhelpers',
    download_url='https://github.com/davidslusser/django-handyhelpers/archive/0.2.tar.gz',
    keywords=['django', 'helpers', ],
    classifiers=[],
    install_requires=[
        'django-extensions',
        'django-filter',
        'django-filters',
        'django-model-utils',
        'django-rest-swagger',
        'djangorestframework-filters',
        'djangorestframework',
        'simple-crypt',
        'model-mommy',
    ],
    dependency_links=[],
)
