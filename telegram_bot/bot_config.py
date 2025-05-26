import toml

with open("bot_config.toml", "r") as f:
    config = toml.load(f)

BOT_TOKEN = config["credentials"]["BOT_TOKEN"]
API_LINK = config["credentials"]["API_LINK"]
MINI_APP_LINK = config["credentials"]["MINI_APP_LINK"]
