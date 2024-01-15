# haxko_reminder_bot

This bot writes appointment reminder messages to the Telegram channel with a specific ID under the name associated with a specific API token. The decision if a message is written and the exact structure of the message is based on the current system time.

The regular execution of the bot is done by a systemd timer unit (but could also be done e.g. by Cron).

To start the bot, do the following:
1. Copy `haxko_reminder_bot.py` in a new directory in the user's directory.
1. Create the file `api_token.txt` in the same directory as `haxko_reminder_bot.py`. It must contain a single line with the ID of the bot. More information can be found [here](https://core.telegram.org/bots).
1. Create the file `chat_id.txt` also in the same directory as `haxko_reminder_bot.py`. It must contain a single line with the ID of the chat. This ID can e.g. be retrieved by first making the bot part of the channel and than executing `wget https://api.telegram.org/bot<api_token>/getUpdates`. The chat ID is contained in the JSON output.
1. Copy the .service and the .timer file to `/etc/systemd/system`
1. Register the service unit and the timer unit: `systemctl enable haxko_reminder_bot.service` and `systemctl enable haxko_reminder_bot.timer`
1. Start the service unit and the timer unit: `systemctl start haxko_reminder_bot.service` and `systemctl start haxko_reminder_bot.timer`
