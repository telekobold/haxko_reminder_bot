# haxko_reminder_bot

A small bot for publishing public haxko e.V. appointments on Telegram

This bot writes appointment reminder messages to the Telegram channel with a specific ID under the name associated with a specific API token. The decision if a message is written and the exact structure of the message is based on the current system time.

The regular execution of the bot is done externally, e.g. by a systemd Timer unit or Cron.
