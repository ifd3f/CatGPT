#!/usr/bin/env python

import asyncio
import os
import sys

from datetime import datetime
from random import choice, randint

from pleroma import Pleroma


async def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} {{reply, post}}')
        sys.exit(-1)

    match sys.argv[1]:
        case 'post':
            msg = generate_any()
            print(msg)
            async with mk_pleroma() as pl:
                await pl.post(msg, visibility='unlisted')

        case 'reply':
            async with mk_pleroma() as pl:
                await reply_loop(pl)


async def reply_loop(pleroma: Pleroma):
    print("Listening to notifications...")
    async for notification in pleroma.stream_mentions():
        status = notification['status']
        print(f"Handling notification {status['uri']}")
        toot = generate_any()
        await pleroma.reply(status, toot)


def mk_pleroma() -> Pleroma:
    server_url = os.environ["SERVER_URL"]
    access_token = os.environ["ACCESS_TOKEN"]
    return Pleroma(api_base_url=server_url, access_token=access_token)


def generate_nyaa():
    m = randint(1, 6)
    n = randint(1, 15)
    return 'nya' * m + 'ny' + 'a' * n


def generate_mew():
    return 'mew' * randint(1, 6)


def generate_meow():
    return 'meow' * randint(1, 6)


def generate_chinese():
    return '喵' * randint(1, 6)


def generate_japanese():
    return 'ニャン' * randint(1, 3)


def generate_spanish():
    return 'ña' * randint(1, 6)


def pick_generator():
    if randint(1, 10) == 1:
        return choice([
            generate_spanish,
            generate_chinese,
            generate_japanese,
        ])

    return choice([
        generate_nyaa,
        generate_nyaa,
        generate_nyaa,
        generate_mew,
        generate_mew,
        generate_mew,
        generate_meow,
        generate_meow,
        generate_meow,
    ])


def generate_any():
    return ' '.join([
        pick_generator()()
        for i in range(randint(1, 10))
    ])


if __name__ == '__main__':
    asyncio.run(main())

