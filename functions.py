
import re
import logging
import config


def title_contains_artist(artist, title):
    title = re.split("[^{a-z}]+", title)
    artist = re.split("\s", artist)
    length = len(artist)
    for i in range(len(title) - length + 1):
        if title[i:i + length] == artist:
            return True
    return False


def send_message(client, user, deal, artist):
    try:
        title = deal.title
        message = f'Hey looks like there is a new deal on {artist}!\n\n' \
                  f'[{title}](https://reddit.com{deal.permalink})'
        client.redditor(user).message(title, message)
        logging.info(f'Message successfully sent regarding the deal {title}')
    except Exception as e:
        logging.warning(f'Unable to send a message regarding the deal {title}')
        logging.info(e)
        return False


def run_bot(client, artists):
    subreddit = client.subreddit('VinylDeals')
    while True:
        for deal in subreddit.stream.submissions():
            title = deal.title.replace('Lowest', '', 1)
            for artist in artists:
                send_message(client, config.endUser, deal, artist) and logging.info(f'Found a deal on {title}') if title_contains_artist(artist, title.lower()) else None
