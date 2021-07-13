#!/usr/bin/env python

###################################################################
#
# Author: Jeremy Parente
#
# Basic "main" function to test REST API
#
###################################################################


def main(cls):
    import argparse, getpass

    try:
        import IPython
    except ImportError:
        import pdb

        debug = pdb.set_trace
    else:
        debug = IPython.embed

    parser = argparse.ArgumentParser(description="Test FAP REST API")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password")
    parser.add_argument("ADDRESS")
    args = parser.parse_args()

    if args.password is None:
        password = getpass.getpass("Enter %r password:" % args.username)
    else:
        password = args.password

    rest = cls()
    rest.login(args.ADDRESS, args.username, password)
    debug()
    return 0
