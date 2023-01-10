#!/usr/bin/env python

import asyncio
import os
import sys

from datetime import datetime
from random import choice, randint

from pleroma import Pleroma


async def main():
    msg = generate_any()
    print(msg)

    server_url = os.environ["SERVER_URL"]
    access_token = os.environ["ACCESS_TOKEN"]
    async with Pleroma(api_base_url=server_url, access_token=access_token) as pl:
        await pl.post(msg, visibility='unlisted')


def generate_nyaa():
    m = randint(1, 6)
    n = randint(1, 15)
    return 'nya' * m + 'ny' + 'a' * n


def generate_mew():
    n = randint(1, 6)
    return 'mew' * n


def generate_meow():
    n = randint(1, 6)
    return 'meow' * n


def generate_any():
    return ' '.join([
        choice([
            generate_nyaa,
            generate_mew,
            generate_meow,
        ])()

        for i in range(randint(1, 3) * randint(1, 3))
    ])


if __name__ == '__main__':
    asyncio.run(main())

