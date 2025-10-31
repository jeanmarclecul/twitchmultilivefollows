# Twitch multi on live follows

## create twtich app

- create an app : [https://dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps)
- with redir OAuth : http://localhost:3000
- get <client_id> and <secret_id>

## install twitch cli

- scoop bucket add twitch https://github.com/twitchdev/scoop-bucket.git
- scoop install twitch-cli
- twitch configure
- log in with <client_id> and <secret_id>

fill .env with

```ini
CLIENT_ID=
SECRET_ID=
```

## Launch multitwitch link

install dependencies : pip install dotenv

- python get_token.py
- python multitwitch.py
