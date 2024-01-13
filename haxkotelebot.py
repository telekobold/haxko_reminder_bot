import shelve
import datetime

# TODO: MIT-Lizenz hier rein packen

# TODO: Die aktuelle Funktionalität nochmal refactoren und daraus den ersten Commit bauen

# Versionieren:
# 1. Version: Funktionierende Benachrichtigungs-Logik nur als Konsolenoutput (ohne Telegram-Post)
# 2. Version: Telegram-Post
# 3. Version: Weitere Funktionen, z.B. Telegram-Haxko-Eule

# This script is written in such a way that it also works if it didn't run for any period of time.
# Caution: datetime.datetime.today().weekday() returns values between 0 and 6, while datetime.datetime.today.day() returns values starting from 1.
# TODO: Script als Cronjob eintragen
# TODO: Script als Shell-Skript schreiben

MONDAY: int = 0
FRIDAY: int = 4
SATURDAY: int = 5
db: shelve.DbfilenameShelf = shelve.open("haxkotelebot_storage")

NOTIFICTAION_PERIOD = 3 # Time period in days from which notification is to be sent

# This script can easily be tested by adding or subtracting a timedelta to/from today:
# Note: Before some of the test runs, the file haxkotelebot_storage must be deleted since its content probably prevents the execution of the program.
# TODO: Anhand eines Vergleichs des errechneten Meeting-Tages mit dem aktuellen Tag zusätzlich ein "(übermorgen)", "(morgen)" oder "(heute)" ausgeben.
today: datetime.datetime = datetime.datetime.today() + datetime.timedelta(days=10)
print(f"today = {today}")
today_weekday: int = today.weekday()
in_three_days: datetime.datetime = today + datetime.timedelta(days=3)
curr_week: int = today.isocalendar().week

def is_even(n: int) -> bool:
    return n % 2 == 0

def is_before_friday(day: datetime.datetime) -> bool:
    return day.weekday() <= 4

# Der nur auf den Wochentagen basierende Check sollte auch monats- und jahresübergreifend funktionieren:
def is_in_notification_period(day: int) -> bool:
    potential_next_appointment_in: int = day - today.weekday()
    potential_next_appointment: datetime.datetime = today + datetime.timedelta(potential_next_appointment_in)
    #print(f"day = {day}")
    #print(f"potential_next_appointment_in = {potential_next_appointment_in}")
    #print(f"potential_next_appointment = {potential_next_appointment}")
    if day == FRIDAY and potential_next_appointment_in <= NOTIFICTAION_PERIOD and is_friday(potential_next_appointment):
        return potential_next_appointment
    elif day == SATURDAY and potential_next_appointment_in <= NOTIFICTAION_PERIOD and is_saturday(potential_next_appointment):
        return potential_next_appointment
    return None

#def is_in_notification_period(date: datetime.datetime) -> bool:
#    return (date - today).days <= 3

def is_friday(day: datetime.datetime) -> bool:
    return day.weekday() is FRIDAY

def is_saturday(day: datetime.datetime) -> bool:
    return day.weekday() is SATURDAY

def is_friday_or_saturday(day: datetime.datetime) -> bool:
    return is_friday(day) or is_saturday(day)

def check_and_write_msg() -> None:
    global db
    # Check if message_written and message_written_date exist and create them if not:
    if not "message_written" in db:
        db["message_written"]: bool = False
    if not "message_written_date" in db:
        db["message_written_date"]: datetime.datetime = None
    # Ermögliche, dass nach Ablauf des aktuellen Termins eine Benachrichtigung für den nächsten Termin gesendet werden kann (starte eine neue checking period):
    if db["message_written"] is True and db["message_written_date"] is not None and (today - db["message_written_date"]).days > NOTIFICTAION_PERIOD:
    # and (today - db["message_written_date"]).days > NOTIFICTAION_PERIOD:
        db["message_written"] = False
    # Write a new message if it is to be written:
    # Check if no message has already been written:
    if db["message_written"] is False:
        potential_next_appointment_fr: datetime.datetime = is_in_notification_period(FRIDAY)
        potential_next_appointment_sa: datetime.datetime = is_in_notification_period(SATURDAY)
        # Among other things, it must be checked whether the current time is before the meeting or at least on the same day as the meeting:
        if potential_next_appointment_fr is not None and is_even(curr_week) and today <= potential_next_appointment_fr:
            write_msg("Freitag", potential_next_appointment_fr)
        #elif is_saturday(in_three_days): #and not is_even(curr_week):
        elif potential_next_appointment_sa is not None and not is_even(curr_week) and today < potential_next_appointment_sa:
            write_msg("Samstag", potential_next_appointment_sa)

def write_msg(meeting_day: str, next_appointment: datetime.datetime) -> None:
    global db
    meeting_date: str = next_appointment.strftime("%Y-%m-%d")
    # TODO: Post a new message in Telegram
    print(f"Am {meeting_day}, dem {meeting_date} findet wieder ein Haxko-Treffen statt.")
    db["message_written"] = True
    a = type(db["message_written_date"])
    print(f"type(db[\"message_written_date\"]) = {a}")
    print(f"type(today) = {type(today)}")
    db["message_written_date"] = today

def main():
    check_and_write_msg()
    db.close()

if __name__ == "__main__":
    main()
