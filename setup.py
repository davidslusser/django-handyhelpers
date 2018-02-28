from setuptools import setup
import handyhelpers

setup(
    name='django_handy_helpers',
    version=handyhelpers.__version__,
    packages=['handyhelpers'],
    license=handyhelpers.__license__,
    long_description='A collection of handy utilities to support django operations',
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
    dependency_links=[

    ]
)
