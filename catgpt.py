#!/usr/bin/env python3 -u

import asyncio
import os
import sys

from datetime import datetime
from random import choice, randint

from pleroma import Pleroma, BadRequest


MAX_THREAD_LENGTH = 20
MAX_RETRIES = 5


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
            print("Starting reply loop...")
            async with mk_pleroma() as pl:
                await reply_loop(pl)


async def reply_loop(pleroma: Pleroma):
    myself = (await pleroma.me())['id']
    print(f"I am ID {myself}")
    print("Listening to notifications...")

    async for notification in pleroma.stream_mentions():
        retries = 0
        try:
            print(f"Handling notification {notification['status']['id']}")
            await handle_notif(pleroma, myself, notification)
        except BadRequest:
            if retries >= MAX_RETRIES:
                print("  Max retries reached, skipping this post")
                continue

            retries += 1
            print(f"  Attempt {retries} failed, backing off and retrying")
            await asyncio.sleep(2 ** retries)


async def handle_notif(pleroma, myself, notification):
    post_id = notification['status']['id']

    context = await pleroma.status_context(post_id)
    length = get_thread_length(context, myself, MAX_THREAD_LENGTH)
    print(f"  Thread length is {length}")
    if length:
        print("  Reached max thread length, refusing to reply")
        return

    toot = generate_any()
    print(toot)
    await pleroma.reply(notification['status'], toot)


def get_thread_length(context, myself, max_thread: int) -> bool:
    posts = 0
    for post in context['ancestors']:
        if post['account']['id'] == myself:
            posts += 1
        if posts >= max_thread:
            return posts
    return posts


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


def pick_generator():
    if randint(1, 15) == 1:
        return choice([
            lambda: "ня" * randint(1, 6),
            lambda: "ニャン" * randint(1, 6),
            lambda: "喵" * randint(1, 6),
            lambda: "ña" * randint(1, 6)
        ])

    return choice([
        generate_nyaa,
        generate_mew,
        generate_meow,
    ])


def generate_any():
    return ' '.join([
        pick_generator()()
        for i in range(randint(1, 8))
    ])


if __name__ == '__main__':
    asyncio.run(main())

