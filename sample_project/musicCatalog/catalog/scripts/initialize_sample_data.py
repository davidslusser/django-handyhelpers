"""
Description:
    populate your local database with sample data

"""

# import system modules
import argparse
import logging
import os
import sys
from datetime import datetime
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "musicCatalog.settings")
django.setup()

logger = logging.getLogger("script")

__version__ = "0.0.1"


class Struct:
    """ Creates an object from a dictionary """
    def __init__(self, **entries):
        """ Class entry point"""
        self.cloud = None
        self.__dict__.update(entries)


def get_opts():
    """ Return an argparse object. """
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--verbose', default=logging.INFO, action='store_const',
                        const=logging.DEBUG, help="enable debug logging")
    parser.add_argument('--version', action='version', version=__version__)
    args = vars(parser.parse_args())
    logging.basicConfig(level=args["verbose"])
    logger.setLevel(args["verbose"])
    return Struct(**args)


def populate_users():
    """ """
    pass

def populate_groups():
    """ """
    pass

def populate_genres():
    """ """
    pass

def populate_artists():
    """ """
    pass

def populate_albums():
    """ """
    pass

def populate_songs():
    """ """
    pass

def populate_favorites():
    """ """
    pass


def main():
    """ script entry point """
    logger.info("Starting script")
    start_time = datetime.now()
    opts = get_opts()
    populate_groups()
    populate_users()
    populate_groups()
    populate_artists()
    populate_albums()
    populate_songs()
    populate_favorites()
    end_time = datetime.now() - start_time
    logger.info("")
    logger.info("Script completed in: %s", end_time)


if __name__ == "__main__":
    sys.exit(main())