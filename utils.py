import json
import os

discord_secret_path = os.path.abspath('credentials/discord_bot_secret.json')


def load_discord_secret(filename):
    data = None
    with open(filename) as f:
        data = json.load(f)

    if not data:
        raise Exception('Cannot load discord secret')

    discord_bot_secret = data['discord_bot_secret']

    return discord_bot_secret
