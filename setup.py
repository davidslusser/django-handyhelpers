import os
from setuptools import setup, find_packages
import djangohelpers


with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='django-handyhelpers',
    description='A collection of handy utilities to support django operations',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    version=djangohelpers.__version__,
    license=djangohelpers.__license__,
    author=djangohelpers.__author__,
    author_email=djangohelpers.__email__,
    url='https://github.com/davidslusser/django-handyhelpers',
    download_url='https://github.com/davidslusser/django-handyhelpers/archive/{}.tar.gz'
                 ''.format(djangohelpers.__version__),
    keywords=['django', 'helpers', 'handyhelpers'],
    install_requires=required,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 2.2+',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.x',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
