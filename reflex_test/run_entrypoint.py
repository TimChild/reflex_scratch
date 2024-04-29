"""
Entrypoint when debugging (effectively the same as `reflex run`)
"""

import os

import logging

from reflex.reflex import _run


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    _run()
