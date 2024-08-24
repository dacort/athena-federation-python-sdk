#!/usr/bin/env python

import os
import sys


def main():
    print("Hello from athena_federation!")
    print("Arguments: ", sys.argv)
    print("Environment: ", os.environ["VIRTUAL_ENV"])


if __name__ == "__main__":
    main()
