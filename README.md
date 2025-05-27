## Requirements
uv and npm


## build static webapp

```
cd static/webapp
npm install
npm run build
```

## run api

```
cp api/config.toml.template api/config.template (change as you like)
uv sync
uv run uvicorn api.main:app --reload
```

## run telegram bot while webapp is running

```
cp telegram_bot/bot_config.toml.template telegram_bot/bot_config.toml (add credetinals)
uv run python -m telegram_bot.main
```