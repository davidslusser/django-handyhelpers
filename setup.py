import os
from setuptools import setup, find_packages
import djangohelpers

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

setup(
    name='django-handyhelpers',
    packages=find_packages(),
    include_package_data=True,
    version=djangohelpers.__version__,
    license=djangohelpers.__license__,
    author='David Slusser',
    author_email='dbslusser@gmail.com',
    description='A collection of handy utilities to support django operations',
    long_description=README,
    url='https://github.com/davidslusser/django-handyhelpers',
    download_url='https://github.com/davidslusser/django-handyhelpers/archive/0.0.7.tar.gz',
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
