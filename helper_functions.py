import random
import math
import re

import discord


def next_level(level):
    return int(round(230 * level * math.sqrt(level), -2)) + 13000 * (level // 11) + 1000 * (level // 6)


NEXT_XP = {i: next_level(i) for i in range(5000)}


def get_crate_chance(number):
    if number < 1:
        return '>1'
    else:
        return f"{number: >2}"


def round_to_multiple(number, multiple):
    return multiple * math.ceil(number / multiple)


def int_to_roman(number):
    num = [1, 4, 5, 9, 10, 40, 50, 90,
           100, 400, 500, 900, 1000]
    sym = ["I", "IV", "V", "IX", "X", "XL",
           "L", "XC", "C", "CD", "D", "CM", "M"]
    i = 12

    roman_number = ""
    while number:
        div = number // num[i]
        number %= num[i]

        while div:
            roman_number += sym[i]
            div -= 1
        i -= 1

    return roman_number


def get_pretty_time(seconds):
    """Returns a string with the formatted time. If a unit of time is 0 (ex. 0 minutes, it wont be included.)
    Example:
    get_pretty_time(60) -> '1m'
    get_pretty_time(61) -> '1m 1s'
    get_pretty_time(3600) -> '1h'
    get_pretty_time(3601) -> '1h 1s'
"""
    if seconds <= 0:
        return '0s'

    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    time_text = ""

    if weeks:
        time_text += f"{weeks}w "
    if days:
        time_text += f"{days}d "
    if hours:
        time_text += f"{hours}h "
    if minutes:
        time_text += f"{minutes}m "
    if seconds:  # if called with 0 returns 0s
        time_text += f"{seconds}s "

    return time_text[0:-1]


def random_float(a, b):
    return random.randint(a * 100, b * 100)/100


def get_recipe_text(recipe):
    from itemIDs_dictionaries import ITEMS
    return ' + '.join([f"{amount} {ITEMS[item_id]['emoji']} " for item_id, amount in recipe])


def get_number_emoji(number):
    # Made by bee
    if number == 1:
        return '1️⃣'

    elif number == 2:
        return '2️⃣'

    elif number == 3:
        return '3️⃣'

    elif number == 4:
        return '4️⃣'

    elif number == 5:
        return '5️⃣'

    elif number == 6:
        return '6️⃣'

    elif number == 7:
        return '7️⃣'

    elif number == 8:
        return '8️⃣'

    elif number == 9:
        return '9️⃣'

    elif number == 10:
        return '🔟'

    elif number == 0:
        return '0️⃣'


time_format_regex = re.compile("[0-9]+[dhms]")


def cooldown_to_seconds(text):
    numbers = time_format_regex.findall(text)
    times = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}
    return sum([int(amount[:-1]) * times[amount[-1]] for amount in numbers])


def get_all_cooldowns_from_cd_embed(embed: discord.Embed):
    cooldowns = dict()
    embed = embed.to_dict()

    for field in embed['fields']:
        lines = field['value'].split('\n')
        for line in lines:
            command = line.split('`')[1].split(' ')[0]

            if ':white_check_mark:' in line:  # Cooldown ready already
                cooldowns[command] = 0
                continue

            else:
                remaining = line.split('(**')[1].replace('**)', '')
                cooldowns[command] = cooldown_to_seconds(remaining)

    return cooldowns