import toml
from math import isclose

with open("config.toml", "r") as f:
    config = toml.load(f)

# Currency awarded for consecutive messages
CURRENCY_AWARDED = {
    1: config["currency_awarded"]["currency_1"],
    2: config["currency_awarded"]["currency_2"],
    3: config["currency_awarded"]["currency_3"]
}

lootbox_cost = config["lootbox"]["cost"]
lootbox_rarities = config["lootbox"]["rarities"]
lootboxes = [{"rarity" : lootbox_rarity,
              "probability" : config["lootbox"][lootbox_rarity + "_p"],
              "reward" : config["lootbox"][lootbox_rarity + "_r"],
              }for lootbox_rarity in lootbox_rarities]

assert isclose(sum([lootbox["probability"] for lootbox in lootboxes]),1), f"Probabilities must sum to 1 but sum is {sum([lootbox['probability'] for lootbox in lootboxes])}"

BOT_TOKEN = config["credentials"]["BOT_TOKEN"]
MINI_APP_LINK = config["credentials"]["MINI_APP_LINK"]
