import logging
import shelve
import datetime
import requests

# This bot is written in such a way that it also works if it didn't run for any period of time.
# Caution: datetime.datetime.today().weekday() returns values between 0 and 6, while datetime.datetime.today.day() returns values starting from 1.

MONDAY: int = 0
FRIDAY: int = 4
SATURDAY: int = 5
date_format = "%Y-%m-%d %H:%M:%S"

NOTIFICTAION_PERIOD = 3 # Time period in days from which notification is to be sent

# NOTE: This script can easily be tested by adding or subtracting a timedelta to/from today:
# NOTE: For some test runs, the file bot_storage must be deleted since its content probably prevents the execution of the program.
today: datetime.datetime = datetime.datetime.today() + datetime.timedelta(days=10)
print(f"today = {today.strftime(date_format)}")
today_weekday: int = today.weekday()
in_three_days: datetime.datetime = today + datetime.timedelta(days=3)
curr_week: int = today.isocalendar().week

def is_even(n: int) -> bool:
    return n % 2 == 0

def is_before_friday(day: datetime.datetime) -> bool:
    return day.weekday() <= 4

def is_in_notification_period(day: int) -> bool:
    potential_next_appointment_in: int = day - today.weekday()
    potential_next_appointment: datetime.datetime = today + datetime.timedelta(potential_next_appointment_in)
    if day == FRIDAY and potential_next_appointment_in <= NOTIFICTAION_PERIOD and is_friday(potential_next_appointment):
        return potential_next_appointment
    elif day == SATURDAY and potential_next_appointment_in <= NOTIFICTAION_PERIOD and is_saturday(potential_next_appointment):
        return potential_next_appointment
    return None

def is_friday(day: datetime.datetime) -> bool:
    return day.weekday() is FRIDAY

def is_saturday(day: datetime.datetime) -> bool:
    return day.weekday() is SATURDAY

def is_friday_or_saturday(day: datetime.datetime) -> bool:
    return is_friday(day) or is_saturday(day)

def check_and_write_msg() -> None:
    logger.info("Start checking...")
    # Check if message_written and message_written_date exist and create them if not (relevant if the script is started for the first time or if bot_storage was deleted):
    if not "message_written" in db:
        db["message_written"]: bool = False
    if not "message_written_date" in db:
        db["message_written_date"]: datetime.datetime = None
    # Enable a notification to be sent for the next appointment after the last appointment is over:
    if db["message_written"] is True and db["message_written_date"] is not None and (today - db["message_written_date"]).days > NOTIFICTAION_PERIOD:
        db["message_written"] = False
    # Write a new message if it is to be written:
    if db["message_written"] is False: # Check if no message has already been written for the next meeting
        potential_next_appointment_fr: datetime.datetime = is_in_notification_period(FRIDAY)
        potential_next_appointment_sa: datetime.datetime = is_in_notification_period(SATURDAY)
        # Among other things, a post may only be sent if the current time is before the meeting or at least on the same day as the meeting:
        if potential_next_appointment_fr is not None and is_even(curr_week) and today <= potential_next_appointment_fr:
            write_msg("Freitag", potential_next_appointment_fr)
        elif potential_next_appointment_sa is not None and not is_even(curr_week) and today < potential_next_appointment_sa:
            write_msg("Samstag", potential_next_appointment_sa)

def write_msg(meeting_day: str, next_appointment: datetime.datetime) -> None:
    # Retrieve this bot's API token and the chat ID of the Telegram channel to post messages to:
    # The strip() is necessary to remove the trailing '\n' delivered by readline():
    with open("api_token.txt", "r") as f:
        api_token = f.readline().strip()
    with open("chat_id.txt", "r") as f:
        chat_id = f.readline().strip()
    meeting_date: str = next_appointment.strftime("%Y-%m-%d")
    meeting_day_en = "Friday" if meeting_day == "Freitag" else "Saturday"
    text_str: str = f"Am {meeting_day}, dem {meeting_date} findet ab 18:00 Uhr wieder ein haxko-Treffen statt. Weitere Informationen unter https://haxko.space.\nThe next haxko meeting will take place on {meeting_day_en} {meeting_date} from 6 pm. More information at https://haxko.space."
    url = f"https://api.telegram.org/bot{api_token}/sendMessage?chat_id={chat_id}&text={text_str}"
    logger.info("Trying to post reminding message...")
    logger.info(requests.get(url).json())
    db["message_written"] = True
    db["message_written_date"] = today

if __name__ == "__main__":
    # Set up logging to log file haxko_reminder_bot.log and stdout:
    logger: logging.Logger = logging.getLogger("haxko_reminder_bot")
    logger.setLevel(logging.INFO)
    formatter: logging.Formatter = logging.Formatter("%(asctime)s - %(message)s", datefmt=date_format)
    c_handler: logging.StreamHandler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_handler.setFormatter(formatter)
    f_handler: logging.FileHandler = logging.FileHandler("haxko_reminder_bot.log")
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(formatter)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    db: shelve.DbfilenameShelf = shelve.open("bot_storage")
    check_and_write_msg()
    db.close()
