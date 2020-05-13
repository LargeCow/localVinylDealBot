
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
        message = 'Hey looks like there is a new deal on {0}!\n\n'.format(artist) \
                  '[{0}](https://reddit.com{1})'.format(title, deal.permalink)
        client.redditor(user).message(title, message)
        logging.info('Message successfully sent regarding the deal {0}'.format(title))
    except Exception as e:
        logging.warning('Unable to send a message regarding the deal {0}'.format(title))
        logging.info(e)
        return False


def run_bot(client, artists):
    subreddit = client.subreddit('VinylDeals')
    while True:
        for deal in subreddit.stream.submissions():
            title = deal.title.replace('Lowest', '', 1)
            for artist in artists:
                send_message(client, config.endUser, deal, artist) and logging.info('Found a deal on {0}'.format(title)) if title_contains_artist(artist, title.lower()) else None
