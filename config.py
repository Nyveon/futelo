import toml

with open("config.toml", "r") as f:
    config = toml.load(f)

# Currency awarded for consecutive messages
CURRENCY_AWARDED = {
    1: config["currency_awarded"]["currency_1"],
    2: config["currency_awarded"]["currency_2"],
    3: config["currency_awarded"]["currency_3"]
}
