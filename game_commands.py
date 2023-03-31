import asyncio
import collections
import copy
import difflib
import itertools

import discord.ui
from captcha.image import ImageCaptcha

import boss_logics
from boss_logics import BOSSES
from database_functions import *
from global_variables import *
from itemIDs_dictionaries import *


async def is_in_command(channel, user_id):
    try:
        command_id = DATA_CACHE[user_id]['cmd']
        if command_id:
            await channel.send(
                f"<@{user_id}> Don't spam! Wait at least 1 second after using `{COMMANDS[command_id]['name']}`!")
            return True
        return False

    except KeyError:
        DATA_CACHE[user_id] = {'cmd': 0}
        return


async def is_in_command_interaction(interaction: discord.Interaction):
    try:
        command_id = DATA_CACHE[interaction.user.id]['cmd']
        if command_id:
            await interaction.response.send_message(
                content=f"<@{interaction.user.id}> Don't spam! Wait at least 1 second after using "
                        f"`{COMMANDS[command_id]['name']}`!")
            return True

        return False

    except KeyError:
        DATA_CACHE[interaction.user.id] = {'cmd': 0}
        return


async def send_captcha(channel: discord.TextChannel,
                       author: discord.User,
                       interaction: discord.Interaction = None):
    number = str(random.randint(1000, 9999))
    image = ImageCaptcha(fonts=['ANDYB.ttf'])

    data = image.generate(number, format='png')
    file = discord.File(data, filename='magic.png')

    if interaction and interaction.command:
        captcha_message = await interaction.edit_original_response(
            content=f"**Necro:** Hey {author.mention}>, solve this magic riddle!\nWhat are the 4 numbers in this image?",
            attachments=[file])
    else:
        captcha_message = await channel.send(
            content=f"**Necro:** Hey {author.mention}, solve this magic riddle!\nWhat are the 4 numbers in this image?",
            file=file)

    def check(message):
        return (message.author.id == author.id and
                message.channel.id == channel.id)

    attempts = 0
    while True:
        try:
            response = await bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return

        if response.content != number:
            attempts += 1
            if attempts == 3:
                await channel.send("You failed")

        else:
            await channel.send("Correct!")
            return


async def val_help(channel: discord.TextChannel,
                   author: discord.User,
                   command: str,
                   interaction: discord.Interaction = None,
                   return_embed=False):
    embed = discord.Embed(colour=0x962f27, description="")
    embed.set_author(name=f"{author.name}'s help", icon_url=author.avatar)
    embed.set_footer(text="Remember to add 'val' in front of any command!")

    if not interaction:
        parameters = command.split()[2:]
    else:
        if 'options' in interaction.data:
            parameters = interaction.data['options'][0]['value'].split()
        else:
            parameters = []

    topic = ' '.join(parameters)
    item_id, category = get_it_from_name(topic)

    if category == 'weapon':
        emoji = bot.get_emoji(int(WEAPONS[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_weapon_info_text(item_id, 0)

    elif category == 'pickaxe':
        emoji = bot.get_emoji(int(PICKAXES[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_pickaxe_info_text(item_id, 0)

    elif category == 'helmet':
        emoji = bot.get_emoji(int(HELMETS[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_helmet_info_text(item_id, 0)

    elif category == 'armor':
        emoji = bot.get_emoji(int(ARMORS[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_armor_info_text(item_id, 0)

    elif category == 'item':
        emoji = bot.get_emoji(int(ITEMS[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_item_info_text(item_id)

    elif category == 'enemy':
        emoji = bot.get_emoji(int(ENEMIES[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_enemy_info_text(item_id)

    elif category == 'battle_enemy':
        emoji = bot.get_emoji(int(BATTLE_ENEMIES[item_id]['emoji'].split(':')[2][:-1]))
        embed.set_thumbnail(url=emoji.url)
        embed.description += general_battle_enemy_info_text(item_id)

    elif topic in ('traits', 'trait'):
        embed.description += f"""**Trait Points**
[WIP] - work in progress

Your traits define how good you are at certain things.
The **traits** are:
💪🏽 **Strength [STR]:**
This is your physical might. It's main gain is increased melee damage, but it also affects your health and defense.
• allows the user to equip heavier armor and weapons;
• +2 damage for every STR point with normal weapons;
• +1 HP for every 3 STR;
• +1 defense for every 2 STR points;

💨 **Agility [AGI]:**
This defines how fast you can move, dodge and attack. It's main gain is increased damage with light weapons, but it also \
allows you to dodge attacks and have multiple turns in battles.
• +1.5 damage for every AGI point with light weapons;
• +0.5% chance to dodge attacks in battle and +0.01% chance to deal critical hits for every point of AGI;
• +1 DEF for every 3 AGI;

💔 **Endurance [END]:**
This is your ability to endure injuries, resist pain and hazards. It's main benefits are health and defense:
• +3 HP for every END point
• +1 defense for every END point

🧠 **Intellect [INT]:**
This defines how smart you are and your ability to use magic. It's main benefits are increased damage with magic and faster ability to learn.
• unlocks mana at 10 INT;
• +1 mana for every INT point;
• 0.5% more XP in all commands for every INT point, but never more than double your level + INT
• increases magic power, dependant on the magic weapon used;

🍀 **Luck [LUK]:**
This is your luck! It defines how lucky you are in the game across all commands. A gambler's best trait!
• increased luck in all commands, like chances to drop items and encounter rare enemies
• +0.08% chance to deal critical hits for every LUK point;

🗣 **Personality [PER]**
This is your personality, your ability to negotiate and influence people. It's main benefits are lower prices and better ability to trade. 
It also unlocks new options in events.
• +1 mana for every 3 PER points
"""
    elif topic == 'house':
        embed.description += """🏠 **House**

A house is required for placing crafting stations. Each house has a limited amount of spaces available, so you need to \
decide what to keep. You can have as many crafting stations of the same type as you want, for example building 2 furnaces \
to smelt items twice as fast!

You can destroy crafting stations using `val destroy`.

🔥 **Furnace management:**
In your house you can also manage your furnaces if you have any, like adding fuel, removing items, etc. You will manage \
the furnace with the [SELECTED] tag, you can switch between furnaces using the dropdown.
Besides the buttons available on the `val house` command, you can use:
- `val add fuel [item name] [amount]` - add fuel into a furnace
- `val remove fuel [amount]` - removes fuel from a furnace
"""
    elif topic == 'heal':
        embed.description += f"""**Healing**:
{EMOJIS['heal']} **Healing items:**
If you just started playing, you can obtain {ITEMS[12]['emoji']} **Fruits** using the `mine` command! You can use `val help [item]` to see if an item \
can heal you, that's something you need to learn!

⌨ **Command to heal:** `val heal`.
This command will use your worst healing items first then use more powerful ones if necessary. It will not heal you more if using another item would mean overhealing.
Use `val heal full` to consume items until your health is full or higher.

Consider using `val use [item] [amount]` to heal using different items!
"""

    elif topic in ('battle', 'bt'):
        embed.description += f"""⚔ **Battle:**
Battle stronger enemies to gain better loot and more XP!

> 🤝 **Party:**

You can join a battle with up to 3 people.
Use `val battle @user1 @user2...`, by @mentioning your friends to join a battle with them. Everyone must have their cooldown ready in \
order to join!

> ⏱ **Turn count:**

You have 1 turn + a bonus from AGI every time to do actions like attacking, using an item, swapping equipment.
The bonus from AGI is + AGI/50. This is lowered by wearing `normal` or `heavy` armors or helmets.
`Example:`
User's AGI: 34
The user has 1 + 34/50 = 1.68 turns each time.
If the turn is not a whole number, it will stack until the user reaches one.
In our scenario the user has 1.68 turns the first time, then they use 1 turn, leaving them with 0.68 turns, at witch point \
the user takes damage from the enemy and the next player's turn begins. The next time they gain 1.68 turns again for a total of 2.36 turns, so they can do 2 actions.
"""
    elif parameters:
        closest_matched = difflib.get_close_matches(topic, ALL_NAMES, 5)
        text = ''
        for word in closest_matched:
            if len(closest_matched) > 0 and word == closest_matched[0]:
                text += f'`{word}`'
            elif len(closest_matched) > 1 and word == closest_matched[-1]:
                text += f' or `{word}`'
            else:
                text += f", `{word}`"

        m_text = f"<@{author.id}> What are you trying to find help for?\n"
        if closest_matched:
            m_text += f"Did you mean: {text}?"
        else:
            m_text += "Check the name of the thing again!"

        if interaction and interaction.command:
            await interaction.edit_original_response(content=m_text)
        else:
            await channel.send(m_text)
        return

    if not parameters:
        embed.description += """**These are the currently available commands:**

**Progress:**
[ `mine` ] - mine for resources using your pickaxe
[ `seek` ] - seek enemies to kill and obtain loot and xp
[ `battle` ] - battle strong enemies for better rewards
[ `progress` ] - advance to higher zones

**Help:**
[ `help [anything]` ] - Check help about anything in the game
[ `recipes` ] - shows all recipes in the game

**Commands:**
[ `profile` ] - shows your profile
[ `inventory` ] - displays your current items
[ `house` ] - shows your current home and crafting stations
[ `traits` ] - view and assigin your trait points
[ `crates` ] - view info about the available crates
[ `build` ] - make a house and crafting stations
[ `explore` ] - explore the zone you are in
[ `craft` ] - craft armors and tools
[ `heal` ] - heal yourself after fights
[ `use` ] - use an item

**Small guide:**
- `mine` to get resources
- `seek` enemies to kill and use Fruit found in mine to heal
- gather resources and craft better pickaxes and armors
- smelt bricks, leather or pies into your furnace
"""
    if return_embed:
        return embed
    else:
        if interaction and interaction.command:
            await interaction.edit_original_response(embed=embed)
        else:
            await channel.send(embed=embed)


async def val_profile(channel: discord.TextChannel,
                      author: discord.User,
                      command: str,
                      interaction: discord.Interaction = None):
    if not interaction:
        parameters = command.split()[2:]
        if parameters and parameters[-1].replace('<@', '').replace('>', '').isnumeric():
            try:
                user = await bot.fetch_user(parameters[-1].replace('<@', '').replace('>', ''))
            except discord.NotFound:
                await channel.send(
                    f"<@{author.id}> The **ID** provided is not a user's discord ID, make sure it's correct!")
                return
        else:
            user = author
    else:
        if 'resolved' in interaction.data:
            user = await bot.fetch_user(int(list(interaction.data['resolved']['users'].keys())[0]))
        else:
            user = author

    original_author_id = author.id
    author = user

    stats = await get_all_player_info(channel, author, ping=original_author_id)
    if not stats:
        return

    area, max_area, hp, max_hp, trait_points, current_xp, level, mana, max_mana = stats
    pickaxe, weapon, helmet, chest = get_all_player_gear(user.id)
    STR, AGI, END, INT, LUK, PER = get_traits(author.id)

    # calculate these every time depending on sword etc
    # STATFORMULA
    attack = 2 * STR * ('normal' == WEAPONS[weapon]['type']) + int(1.5 * AGI * ('light' == WEAPONS[weapon]['type'])) + \
             WEAPONS[weapon]['at']

    defense = HELMETS[helmet]['def'] + ARMORS[chest]['def'] + AGI // 3 + STR // 2 + END

    embed = discord.Embed(colour=ZONES[area]['color'], description="**This is your current progress:**")
    embed.set_author(name=f"{author.name}'s profile", icon_url=author.avatar)
    embed.set_thumbnail(url=random.choice(ZONES[area]['image_link']))
    space_len = max(map(len, [str(i) for i in [STR, AGI, END]]))

    stat_text = f"""
**Currenty in Zone {int_to_roman(area)} {random.choice(ZONES[area]['emoji'])} {ZONES[area]['name']}**
**Highest zone unlocked: {max_area}**

Level: **{level}**
XP: **{current_xp}/{next_level(level)}**
{EMOJIS['hp']} Health: **{hp}/{max_hp}**"""
    if mana:
        stat_text += f"\n{EMOJIS['mana']} Mana: **{mana}/{max_mana}**"

    stat_text += f"""
{EMOJIS['at']} Damage: **{attack}**
{EMOJIS['def']} Defense: **{defense}**
"""

    gear_text = f"""
Pickaxe: {PICKAXES[pickaxe]['emoji']} **{PICKAXES[pickaxe]['name']}**
Weapon: {WEAPONS[weapon]['emoji']}**{WEAPONS[weapon]['name']}**
Helmet: {HELMETS[helmet]['emoji']} **{HELMETS[helmet]['name']}**
Armor: {ARMORS[chest]['emoji']} **{ARMORS[chest]['name']}**

"""
    traits_text = f"""```py
STR: {STR}{' ' * (10 + (space_len - len(str(STR))))}INT: {INT}
AGI: {AGI}{' ' * (10 + (space_len - len(str(AGI))))}LUK: {LUK}
END: {END}{' ' * (10 + (space_len - len(str(END))))}PER: {PER}```"""

    view = discord.ui.View()
    if trait_points and user.id == original_author_id:
        traits_text += f"**You** have **{trait_points}** unspent {EMOJIS['trait']} **Trait Point{'s' if trait_points > 1 else ''}**!"
        view.add_item(discord.ui.Button(label='Assign traits', emoji=EMOJIS['trait'],
                                        custom_id=f'tspend_command{original_author_id}'))
    else:
        view.add_item(discord.ui.Button(label='Traits', emoji=EMOJIS['trait'],
                                        custom_id=f'tspend_command'))

    view.add_item(discord.ui.Button(label='Equipment', emoji=PICKAXES[pickaxe]['emoji'],
                                    custom_id=f'equipment_command'))

    embed.add_field(name="Stats", value=stat_text, inline=False)
    embed.add_field(name="Gear", value=gear_text, inline=False)
    embed.add_field(name="Traits", value=traits_text, inline=False)
    embed.set_footer(text="Use [val help] for the list of all commands")

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed, view=view)
    else:
        await channel.send(embed=embed, view=view)


async def cooldown_warning(channel, author, command_name, time_left, area, interaction=None):
    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name} cooldown!", icon_url=author.avatar)

    hours, remainder = divmod(time_left, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    time_text = ""

    if hours:
        time_text += f"{hours}h "
    if minutes:
        time_text += f"{minutes}m "
    if seconds:
        time_text += f"{seconds}s "
    embed.description = f"""You don't have enough energy to **{command_name}** now!
    
Try again in **{time_text}**"""

    embed.set_footer(text="This command is on cooldown!")

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(embed=embed)


async def val_mine(channel: discord.TextChannel,
                   author: discord.User,
                   interaction: discord.Interaction = None):
    last_used = get_cooldown(author.id, 1)

    area = await get_player_area(channel, author)
    if not area:
        return None

    if time.time() - last_used <= 20.0:
        await cooldown_warning(channel, author, 'mine', 20 - int(time.time() - last_used), area,
                               interaction=interaction)
        return

    STR, AGI, END, INT, LUK, PER = get_traits(author.id)
    pickaxe = await get_player_pickaxe(author.id)

    current_xp, level = get_xp(author.id)
    xp_gained = 0

    found_text = ""
    # The Forest =======================================================================================================
    if area == 1:
        xp_gained = random.randint(level, level + 10)
        if pickaxe == 4:
            xp_gained += int(xp_gained * 0.15)

        items_found = []

        if random_float(1, 100) <= 20 + PICKAXES[pickaxe]['power'] * 5 + LUK * 0.05:
            items_found.append((12, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # 50% chance + PICKAXE_POWER
        if random_float(0, 9) - PICKAXES[pickaxe]['power'] <= 5 + (pickaxe == 1) + LUK * 0.05:
            items_found.append((1, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # 40% chance + PICKAXE_POWER
        if random_float(0, 9) - PICKAXES[pickaxe]['power'] <= 3 + (pickaxe == 2) + LUK * 0.05:
            items_found.append((2, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # 10% chance + PICKAXE_POWER
        if random_float(0, 9) - PICKAXES[pickaxe]['power'] <= 1 + LUK * 0.02:
            items_found.append((5, random.randint(1, int(math.ceil(PICKAXES[pickaxe]['max_items'] / 2)))))

        if pickaxe >= 1:
            if random_float(0, 14) - PICKAXES[pickaxe]['power'] <= 1 + (pickaxe == 3) + LUK * 0.03:
                items_found.append((3, random.randint(1, int(math.ceil(PICKAXES[pickaxe]['max_items'] / 3)))))

            if random_float(0, 120) - PICKAXES[pickaxe]['power'] <= 1 + LUK * 0.05:
                xp_gained += 5
                if pickaxe >= 7:
                    items_found.append((4, random.randint(1, PICKAXES[pickaxe]['power'])))
                else:
                    items_found.append((4, 1))

        # 100% at least 1 DIRT
        if not items_found:
            items_found = [(1, 1)]

        for item_id, amount in items_found:
            if item_id != 4 and amount and pickaxe == 4 and amount < 3:  # pumpkin pick buff
                amount += 1

            found_text += f"**+{amount} {ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}**\n"
            add_item(author.id, item_id, amount)

    # The Desert =======================================================================================================
    elif area == 2:
        xp_gained = random.randint(level + 100, level + 180)

        items_found = []
        if PICKAXES[pickaxe]['power'] <= 2.5:
            PICKAXES[pickaxe]['max_items'] = 1

        # SAND
        if random_float(1, 100) <= 70 + PICKAXES[pickaxe]['power'] + LUK * 0.04:
            items_found.append((16, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # Prickly Pear
        if random_float(1, 100) <= 30 + PICKAXES[pickaxe]['power'] * 2 + LUK * 0.04:
            items_found.append((17, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # CACTUS
        if random_float(1, 100) <= 25 + (pickaxe == 6) + PICKAXES[pickaxe]['power'] * 2 + LUK * 0.04:
            items_found.append((20, random.randint(1, PICKAXES[pickaxe]['max_items'])))

        # BONES
        if PICKAXES[pickaxe]['power'] >= 3 and random_float(1, 100) <= 25 + (pickaxe == 8) + PICKAXES[pickaxe]['power'] + LUK * 0.04:
            items_found.append((21, random.randint(1, int(math.ceil(PICKAXES[pickaxe]['max_items'] / 2)))))

        # COPPER ORE
        if PICKAXES[pickaxe]['power'] >= 3.5 and random_float(1, 100) <= 10 + ((pickaxe == 9) * 5) + PICKAXES[pickaxe]['power'] + LUK * 0.03:
            items_found.append((19, random.randint(1, int(math.ceil(PICKAXES[pickaxe]['max_items'] / 2)))))

        # Mysterious Fragment
        if PICKAXES[pickaxe]['power'] >= 3.5 and random_float(1, 100) <= 0.5 + (pickaxe == 9) + LUK * 0.03:
            items_found.append((19, random.randint(1, int(math.ceil(PICKAXES[pickaxe]['max_items'] / 3)))))

        # 100% at least 1 SAND
        if not items_found:
            items_found = [(16, 1)]

        for item_id, amount in items_found:
            found_text += f"**+{amount} {ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}**\n"
            add_item(author.id, item_id, amount)

    int_xp_extra = int(math.ceil(xp_gained * (INT / 200)))
    xp_gained += int_xp_extra if int_xp_extra < (level + INT) * 2 else (level + INT) * 2

    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name} mines", icon_url=author.avatar)
    embed.description = f"""
**{author.name}** is mining in {random.choice(ZONES[area]['emoji'])} **{ZONES[area]['name']}** using their \
{PICKAXES[pickaxe]['emoji']} **{PICKAXES[pickaxe]['name']}**! 

> You found:

{found_text}**+{xp_gained} XP**
"""

    if xp_gained + current_xp >= NEXT_XP[level]:
        level_up_message(author, current_xp + xp_gained - NEXT_XP[level], level)
        embed.description += f"\n**Leveled up! +5 {EMOJIS['trait']} Trait Points!**"
    else:
        add_xp(author.id, xp_gained)

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed, view=VIEWS['base_select'])
    else:
        await channel.send(embed=embed, view=VIEWS['base_select'])

    update_cooldown(author.id, 1)
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Mine again",
                                    emoji=PICKAXES[pickaxe]['emoji'],
                                    style=discord.ButtonStyle.blurple,
                                    custom_id='mine_command'))

    return view


def level_up_message(author, extra_xp, level):
    level_up(author.id, level + 1, extra_xp)
    return f"**You** leveled up! Acquired **+5 {EMOJIS['trait']} Trait Points**. Assign them using `val traits`!"


async def val_inventory(channel: discord.TextChannel,
                        author: discord.User,
                        command: str, mentions,
                        interaction: discord.Interaction = None,
                        show_zone=0):

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if mentions:
        user = mentions[0]
    else:
        user = author

    original_author_id = author.id
    author = user

    area, max_area = await get_player_max_area(channel, author, ping=original_author_id)
    if not area:
        return

    if show_zone:
        if show_zone > max_area:
            await send_response(content=f"{author.mention}, your max zone is lower than {show_zone}! You can't view the items for that zone!")
            return
        area = show_zone

    items = get_full_inventory_dict(author.id)
    crates = get_user_crates(author.id)

    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s inventory", icon_url=author.avatar)

    inventory_text = ""

    for item_id in SORT_ORDER[area]:
        if item_id in items and items[item_id]:
            inventory_text += f"{ITEMS[item_id]['emoji']} **{ITEMS[item_id]['name']}:** {items[item_id]}\n"

    if not inventory_text:
        inventory_text = "No items. Use `val mine` to get some!"

    embed.add_field(name=f"{random.choice(ZONES[area]['emoji'])} Zone {int_to_roman(area)} items",
                    value=inventory_text + ("ㅤ" if crates else ''),
                    inline=False)

    special_items_text = ""
    for item_id in SPECIAL_ITEMS:
        if item_id in items and items[item_id]:
            special_items_text += f"{ITEMS[item_id]['emoji']} **{ITEMS[item_id]['name']}:** {items[item_id]}\n"

    if crates:
        for crate_id in crates:
            special_items_text += f"{CRATES[crate_id]['emoji']} **{CRATES[crate_id]['name']}:** {crates[crate_id]}\n"

    if special_items_text:
        embed.add_field(name=f"✨ Special Items:",
                        value=special_items_text,
                        inline=False)

    view = discord.ui.View()
    if max_area > 1 and user.id == original_author_id:
        select = discord.ui.Select(placeholder="View items for another zone", custom_id=f"inventory_{author.id}")
        select.options = [discord.SelectOption(label=f"Zone {int_to_roman(i)} items", value=f"{i}",
                                               description=f"View the items found in zone {ZONES[i]['name']}",
                                               emoji=random.choice(ZONES[i]['emoji'])) for i in range(1, max_area+1)]
        view.add_item(select)

    await send_response(embed=embed, view=view)


def get_house_embed(author, area, furnace_selected=-1):
    house = get_player_house(author.id)
    crafting_stations = get_available_crafting_stations_list(author.id)
    has_clickables = False
    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s house", icon_url=author.avatar)

    embed.description = f"""
Current house: **{HOUSES[house]['emoji']} {HOUSES[house]['name']}**
- _{HOUSES[house]['description']}_

__**🛠 Crafting stations:**__
"""

    if not crafting_stations:
        embed.description += "You don't have any crafting stations. Build more with `val build`!\n"

    embed.description += '\n'
    house_slots = {}
    furnaces = get_furnaces_info(author.id)

    view = discord.ui.View()
    for _, station_id, slot_in_house in crafting_stations:
        house_slots[slot_in_house] = station_id

    for slot in range(0, HOUSES[house]['spaces']):
        embed.description += f"> **SLOT {slot + 1}:**\n"

        if slot not in house_slots:
            embed.description += "-- EMPTY --\n\n"
            continue

        station_id = house_slots[slot]
        if 'furnace' in CRAFTING_STATIONS[station_id]:
            if furnace_selected == -1:
                furnace_selected = slot

            embed.description = format_furnace_view(embed.description, furnaces, slot, author.id,
                                                    selected=furnace_selected == slot)

        else:
            embed.description += f"**__{CRAFTING_STATIONS[station_id]['emoji']} {CRAFTING_STATIONS[station_id]['name']}__**\n" \
                                 f"- _{CRAFTING_STATIONS[station_id]['description']}_\n\n"

    embed.set_footer(text="Learn more with [val help house]")

    if furnaces:
        has_clickables = True
        view.add_item(
            discord.ui.Button(label="Add Fuel", emoji='➕', custom_id='add_fuel', style=discord.ButtonStyle.green))

        if furnaces[furnace_selected]['fuel_amount']:
            view.add_item(
                discord.ui.Button(label="Remove Fuel", emoji=ITEMS[furnaces[furnace_selected]['fuel_inside']]['emoji'],
                                  custom_id='remove_fuel',
                                  style=discord.ButtonStyle.red))

        if furnaces[furnace_selected]['item_amount_inside']:
            view.add_item(
                discord.ui.Button(label="Remove Items", emoji=ITEMS[furnaces[furnace_selected]['item_inside']]['emoji'],
                                  custom_id='remove_item',
                                  style=discord.ButtonStyle.red))

        view.add_item(
            discord.ui.Button(label="Refresh", emoji='🔂', custom_id='refresh',
                              style=discord.ButtonStyle.blurple))

        select = discord.ui.Select(placeholder=f"Edit another furnace", custom_id='furnace_select')
        select.options = []

        for furnace_slots in sorted(furnaces):
            select.options.append(discord.SelectOption(
                label=f"SLOT {furnace_slots + 1}",
                emoji=f"{CRAFTING_STATIONS[furnaces[furnace_slots]['furnace_id']]['emoji']}",
                description=f"Edit furnace in slot {furnace_slots + 1}."))

        view.add_item(select)

    return embed, view, furnace_selected, has_clickables


def format_furnace_view(embed_description, furnaces, slot, player_id, selected=False, just_give_rewards=False):
    """My most prized function. Collects items and updates furnace info"""

    last_time_viewed = furnaces[slot]['last_collected']
    time_left_next_fuel = furnaces[slot]['next_fuel']
    time_left_next_item = furnaces[slot]['next_item']

    furnace_id = furnaces[slot]['furnace_id']
    item = furnaces[slot]['item_inside']
    item_amount = furnaces[slot]['item_amount_inside'] - 1
    fuel = furnaces[slot]['fuel_inside']
    fuel_amount = furnaces[slot]['fuel_amount'] - 1

    time_passed = int(time.time()) - last_time_viewed
    smallest_good = min([time_passed,
                         ITEMS[item]['smelt_time'] * item_amount + time_left_next_item,
                         ITEMS[fuel]['fuel_power'] * fuel_amount + time_left_next_fuel])

    time_passed = [smallest_good, smallest_good]

    items_done = 0
    fuel_used = 0

    if item and fuel:
        if time_passed[0] >= ITEMS[item]['smelt_time']:
            items_done += time_passed[0] // ITEMS[item]['smelt_time']
            time_passed[0] -= items_done * ITEMS[item]['smelt_time']

        if time_passed[0] >= time_left_next_item:
            items_done += 1
            time_left_next_item = ITEMS[item]['smelt_time'] - (time_passed[0] - time_left_next_item)

        else:
            time_left_next_item -= time_passed[0]

        if time_passed[1] >= ITEMS[fuel]['fuel_power']:
            fuel_used += time_passed[1] // ITEMS[fuel]['fuel_power']
            time_passed[1] -= fuel_used * ITEMS[fuel]['fuel_power']

        if time_passed[1] > time_left_next_fuel:
            fuel_used += 1
            time_left_next_fuel = ITEMS[fuel]['fuel_power'] - (time_passed[1] - time_left_next_fuel)

        else:
            time_left_next_fuel -= time_passed[1]

    if time_left_next_fuel < 0:
        time_left_next_fuel = 0

    set_furnace_view_last(player_id, slot, time_left_next_fuel, time_left_next_item)

    reward_text = ""
    if items_done:
        reward_text += f"Collected **+{items_done} {ITEMS[item]['emoji']} {ITEMS[item]['name']}** from the furnace.\n"

    saved_item_id = item

    if items_done:
        add_item(player_id, item, items_done)
        remove_done_item_in_furnace(player_id, slot, items_done)
        if items_done == item_amount + 1:
            remove_item_in_furnace(player_id, slot, from_finished=True)
            item = 0
            time_left_next_item = 0
            furnaces[slot]['item_amount_inside'] = 0

    if fuel_used:
        remove_done_fuel_in_furnace(player_id, slot, fuel_used)

    if (not fuel_amount and not time_left_next_fuel) or fuel_used == fuel_amount + 1:
        remove_fuel(player_id, slot, from_finished=True)
        fuel = 0
        fuel_amount = -1
        time_left_next_fuel = 0
        furnaces[slot]['fuel_amount'] = 0

    if just_give_rewards:
        return items_done, saved_item_id

    fuel_amount += 1 - fuel_used
    if fuel_amount < 0:
        fuel_amount = 0

    item_amount += 1 - items_done
    if item_amount < 0:
        item_amount = 0

    embed_description += f"""\
**__{CRAFTING_STATIONS[furnace_id]['emoji']} {CRAFTING_STATIONS[furnace_id]['name']}__** {'**[SELECTED]**' if selected else ''}
**Items to smelt left:** ({get_pretty_time(ITEMS[item]['smelt_time'] * item_amount - (ITEMS[item]['smelt_time'] - time_left_next_item))} total time)
**{ITEMS[item]['emoji']} {ITEMS[item]['name'] if item else ''}:** {item_amount if item_amount else ''} ({get_pretty_time(time_left_next_item)} until next)

**Fuel left:** ({get_pretty_time(ITEMS[fuel]['fuel_power'] * fuel_amount - (ITEMS[fuel]['fuel_power'] - time_left_next_fuel))} total time)
**{ITEMS[fuel]['emoji']} {ITEMS[fuel]['name'] if fuel else ''}:**  {fuel_amount if fuel_amount else ''} ({get_pretty_time(time_left_next_fuel)} until next burns up)

"""

    embed_description += reward_text

    return embed_description


async def val_house(channel: discord.TextChannel,
                    author: discord.User,
                    interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    embed, view, furnace_selected, has_clickables = get_house_embed(author, area)

    if interaction and interaction.command:
        house_embed = await interaction.edit_original_response(embed=embed, view=view)
    else:
        house_embed = await channel.send(embed=embed, view=view)

    if not has_clickables:
        return

    DATA_CACHE[author.id]['house_message_id'] = house_embed.id

    # Modal called when the user presses on "Add fuel"
    add_fuel_modal = discord.ui.Modal(title="Add fuel furnace", custom_id='add_fuel_modal')
    add_fuel_modal.add_item(discord.ui.TextInput(label="What item do you want to add?", style=discord.TextStyle.short))
    add_fuel_modal.add_item(
        discord.ui.TextInput(label="How many items do you want to add?", style=discord.TextStyle.short))

    def check(inter: discord.Interaction):
        return inter.message and inter.message.id == house_embed.id

    while True:
        try:
            interaction: discord.Interaction = await bot.wait_for('interaction', timeout=60, check=check)
        except asyncio.TimeoutError:
            for child in view.children:
                child.disabled = True

            await house_embed.edit(view=view)
            return

        if interaction.message.id != DATA_CACHE[author.id]['house_message_id']:
            for child in view.children:
                child.disabled = True
            await interaction.response.edit_message(view=view)
            return

        if interaction.message and interaction.message.id != house_embed.id:
            continue

        if interaction.user.id != author.id:
            await interaction.response.send_message(
                content="This is not your command! Use `val house` to do this yourself!", ephemeral=True)
            continue

        elif interaction.data['custom_id'] == 'refresh':
            embed, view, _, _ = get_house_embed(author, area, furnace_selected=furnace_selected)
            await interaction.response.edit_message(embed=embed, view=view)

        elif interaction.data['custom_id'] == 'furnace_select':
            furnace_selected = int(interaction.data['values'][0][5]) - 1
            embed, view, _, _ = get_house_embed(author, area, furnace_selected=furnace_selected)
            await interaction.response.edit_message(embed=embed, view=view)

        elif interaction.data['custom_id'] == 'add_fuel':
            await interaction.response.send_modal(add_fuel_modal)

        elif interaction.data['custom_id'] == 'remove_fuel':
            itema, amounta = remove_fuel(author.id, furnace_selected)
            embed, view, _, _ = get_house_embed(author, area, furnace_selected=furnace_selected)
            if amounta:
                embed.description += f"+{amounta} **{ITEMS[itema]['emoji']} {ITEMS[itema]['name']}**"

            await interaction.response.edit_message(embed=embed, view=view)

        elif interaction.data['custom_id'] == 'remove_item':
            itema, amounta = remove_item_in_furnace(author.id, furnace_selected)
            embed, view, _, _ = get_house_embed(author, area, furnace_selected=furnace_selected)
            embed.description += f"+ resources for **{amounta} {ITEMS[itema]['emoji']} {ITEMS[itema]['name']}**"
            await interaction.response.edit_message(embed=embed, view=view)

        elif interaction.data['custom_id'] == 'add_fuel_modal':
            item_name = interaction.data['components'][0]['components'][0]['value'].strip().lower()
            item_amount = interaction.data['components'][1]['components'][0]['value'].strip().lower()

            item_id, item_type = get_it_from_name(item_name)
            if not item_id:
                await interaction.response.send_message("Unknown item submitted, please check the item name again!",
                                                        ephemeral=True)
                continue

            if 'fuel_power' not in ITEMS[item_id]:
                await interaction.response.send_message(
                    "That item is not flammable! Use something like logs, branches, etc. You can use `val help [item]` to see more details about an item.",
                    ephemeral=True)
                continue

            if not item_amount.isnumeric() or int(item_amount) < 1:
                await interaction.response.send_message("Incorrect amount! You must input a whole number!",
                                                        ephemeral=True)
                continue

            current_fuel, _, next_fuel_burn = get_current_fuel_in_furnace(author.id, furnace_selected)
            if current_fuel and current_fuel != item_id:
                await interaction.response.send_message("Please remove the current fuel before adding another type!",
                                                        ephemeral=True)
                continue

            item_amount = int(item_amount)
            inventory = get_full_inventory_dict(author.id)
            if item_id not in inventory or inventory[item_id] < item_amount:
                await interaction.response.send_message(
                    f"You don't have that many **{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}**", ephemeral=True)
                continue

            if not next_fuel_burn:
                add_fuel(author.id, item_id, item_amount, furnace_selected,
                         burn_time=ITEMS[item_id]['fuel_power'])
            else:
                add_fuel(author.id, item_id, item_amount, furnace_selected)

            embed, view, _, _ = get_house_embed(author, area, furnace_selected=furnace_selected)
            await interaction.response.edit_message(embed=embed, view=view)
            continue


async def val_build(channel: discord.TextChannel,
                    author: discord.User,
                    command: str,
                    interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            DATA_CACHE[author.id]['cmd'] = 0
            await val_recipes(channel, author, 'val recipes b')
            return

        item_name = ' '.join(parameters)
    else:
        item_name = ' '.join(interaction.data['options'][0]['value'].split())

    item_id, _type = get_it_from_name(item_name)

    if _type and _type not in ('station', 'house'):
        await send_response(content=f"<@{author.id}> That item is crafted through `val craft`! This command is for making houses and crafting stations")
        return

    if _type == 'house':
        house = get_player_house(author.id)
        if house == item_id:
            await send_response(content=f"<@{author.id}> You already have this house! Check your house with `val house`!")
            return

        elif item_id < house:
            await send_response(content=f"<@{author.id}> You can't downgrade your house!")
            return

        await build_house(channel, author, item_id, area, interaction=interaction)

    elif _type == 'station':
        house = get_player_house(author.id)
        if not house:
            await send_response(
                content=f"<@{author.id}> You don't have a house to put this in! Build one using `/build`. Check the available houses in `/recipes` -> builds")
            return

        stations = get_available_crafting_stations_list(author.id)

        if HOUSES[house]['spaces'] - len(stations) == 0:
            await send_response(
                content=f"<@{author.id}> You don't have more space in your house! Destroy some crafting stations using `/destroy [station name]`!")
            return

        house_slots = []
        for _, station_id, slot_in_house in stations:
            house_slots.append(slot_in_house)

        for slot in range(0, HOUSES[house]['spaces']):
            if slot not in house_slots:
                await build_station(channel, author, item_id, slot, area, interaction=interaction)
                return
    else:
        closest_matched = difflib.get_close_matches(item_name, ALL_CRAFTABLES, 5)
        text = ''
        for word in closest_matched:
            if len(closest_matched) > 0 and word == closest_matched[0]:
                text += f'`{word}`'
            elif len(closest_matched) > 1 and word == closest_matched[-1]:
                text += f' or `{word}`'
            else:
                text += f", `{word}`"

        m_text = f"<@{author.id}> What are you trying to build?\n"
        if closest_matched:
            m_text += f"Did you mean: {text}?"
        else:
            m_text += "Check the name of the build again!"

        m_text += "\nCorrect usage: `/build [build name]`. Check the available builds in `/recipes` -> builds"
        await send_response(content=m_text)


async def build_house(channel, author, house_id, zone, interaction=None):
    inventory = get_full_inventory_dict(author.id)

    # Check if user has everything required
    for item_id, amount in HOUSES[house_id]['recipe']:
        if item_id not in inventory or inventory[item_id] < amount:
            await show_items_left_required(channel, author, HOUSES[house_id]['recipe'],
                                           inventory, zone, interaction=interaction)
            return

    for item_id, amount in HOUSES[house_id]['recipe']:
        remove_item(author.id, item_id, amount)

    set_house(author.id, house_id)

    embed = discord.Embed(colour=ZONES[zone]['color'])
    embed.set_thumbnail(url=author.avatar)
    embed.set_author(name=f"{author.name}'s {HOUSES[house_id]['name'].lower()}", icon_url=author.avatar)
    embed.description = (
            f"✨ **{HOUSES[house_id]['emoji']} {HOUSES[house_id]['name']} successfully built** !✨\n" +
            (f"{HOUSES[house_id]['special_text']}" if 'special_text' in HOUSES[house_id] else ''))
    embed.set_footer(text="Check [val help <house>] for more info!")
    emoji = bot.get_emoji(int(HOUSES[house_id]['emoji'].split(':')[2][:-1]))
    embed.set_image(url=emoji.url)

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(author.mention, embed=embed)


async def build_station(channel, author, station_id, slot_number, zone, interaction=None):
    inventory = get_full_inventory_dict(author.id)

    # Check if user has everything required
    for item_id, amount in CRAFTING_STATIONS[station_id]['recipe']:
        if item_id not in inventory or inventory[item_id] < amount:
            await show_items_left_required(channel, author, CRAFTING_STATIONS[station_id]['recipe'], inventory, zone)
            return

    for item_id, amount in CRAFTING_STATIONS[station_id]['recipe']:
        remove_item(author.id, item_id, amount)

    add_station(author.id, station_id, slot_number)

    embed = discord.Embed(colour=ZONES[zone]['color'])
    embed.set_thumbnail(url=author.avatar)
    embed.set_author(name=f"{author.name}'s {CRAFTING_STATIONS[station_id]['name'].lower()}", icon_url=author.avatar)
    embed.description = (
            f"✨ **{CRAFTING_STATIONS[station_id]['emoji']} {CRAFTING_STATIONS[station_id]['name']} successfully built** !✨\n" +
            (f"{CRAFTING_STATIONS[station_id]['special_text']}" if 'special_text' in CRAFTING_STATIONS[
                station_id] else ''))
    embed.set_footer(text="Check [val help <crafting station>] for more info!")
    emoji = bot.get_emoji(int(CRAFTING_STATIONS[station_id]['emoji'].split(':')[2][:-1]))
    embed.set_image(url=emoji.url)

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(author.mention, embed=embed)


async def show_items_left_required(channel, author, recipe, inventory, zone, amount=1, interaction=None):
    text = f"**__Items required:__** \n"
    for item, amount_in_recipe in recipe:
        if item not in inventory:
            inventory[item] = 0

        text += f"{inventory[item]}/{amount * amount_in_recipe} **{ITEMS[item]['emoji']} {ITEMS[item]['name']}**\n"

    embed = discord.Embed(colour=ZONES[zone]['color'], description=text)
    embed.set_author(name=f"{author.name}'s recipe", icon_url=author.avatar)
    embed.set_footer(text="You don't have the items required to make this!")

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(embed=embed)


async def val_recipes(channel: discord.TextChannel,
                      author: discord.User,
                      command: str,
                      interaction: discord.Interaction = None):
    area, max_area = await get_player_max_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        parameters = command.split()[2:]
    else:
        parameters = []
        if 'options' in interaction.data and interaction.data['options']:
            parameters.append(str(interaction.data['options'][0]['value']))
            if len(interaction.data['options']) > 1:
                parameters.append(str(interaction.data['options'][1]['value']))

    category_dict = {'pickaxe': 'pickaxe', 'p': 'pickaxe', 'pick': 'pickaxe', 'pickaxes': 'pickaxe',
                     'item': 'item', 'i': 'item', 'items': 'item',
                     'armor': 'armor', 'a': 'armor', 'armors': 'armor',
                     'weapons': 'weapon', 'w': 'weapon', 'weapon': 'weapon',
                     'build': 'build', 'b': 'build', 'builds': 'build'}

    wanted_category = "pickaxe"
    wanted_area = 0

    if parameters:
        if parameters[0].isnumeric():
            wanted_area = int(parameters[0])
            if wanted_area > area:
                await send_response(content=f"<@{author.id}> You haven't unlocked that zone yet!")
                return

        elif parameters[0] in category_dict:
            wanted_category = category_dict[parameters[0]]

        else:
            await send_response(content=f"<@{author.id}> What are you trying to do?\n"
                                        f"Correct usage: `val recipes [category] [zone#]`.")
            return

        if len(parameters) == 2 and parameters[1].isnumeric() and not wanted_area:
            wanted_area = int(parameters[1])
            if wanted_area > area:
                await send_response(content=f"<@{author.id}> You haven't unlocked that zone yet!")
                return

        elif len(parameters) == 2 and parameters[1] in category_dict and wanted_category != 'pickaxe':
            wanted_category = category_dict[parameters[1]]

        elif len(parameters) == 2:
            await send_response(content=f"<@{author.id}> What are you trying to do?\n"
                                        f"Correct usage: `val recipes [category] [zone#]`.")
            return

    if not wanted_area:
        wanted_area = area

    CRAFT_MSG = {'item': "Craft them using `val craft [item name]`",
                 'pickaxe': "Craft them using `val craft [pickaxe name]`",
                 'build': "Construct them using `val build [build name]`",
                 'weapon': "Craft them using `val craft [weapon name]\nMake sure you meet the STR requirement!`",
                 'armor': "Craft them using `val craft [armor name]\nMake sure you meet the STR requirement!`"}

    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s recipes", icon_url=author.avatar)
    embed.set_footer(text="Use `val recipes [category] [zone_number]` to check the recipes of other zones!")
    pickaxe = await get_player_pickaxe(author.id)

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(label="Pickaxes", emoji=PICKAXES[pickaxe]['emoji'], custom_id='recipes_pickaxes', row=2))
    view.add_item(discord.ui.Button(label="Weapons", emoji='⚔', custom_id='recipes_weapons', row=2))
    view.add_item(discord.ui.Button(label="Armors", emoji='🧰', custom_id='recipes_armors', row=2))
    view.add_item(discord.ui.Button(label="Items", emoji='🍢', custom_id='recipes_items', row=2))
    view.add_item(discord.ui.Button(label="Builds", emoji='🧱', custom_id='recipes_builds', row=2))

    select = discord.ui.Select(placeholder='View for another zone...', custom_id='recipes_select', row=3)

    for zone in range(1, max_area + 1):
        select.options.append(discord.SelectOption(label=f"Zone {zone}",
                                           description=f"All recipes for {ZONES[zone]['name']}",
                                           emoji=random.choice(ZONES[zone]['emoji']),
                                           value=zone))

    page = 1
    if type(RECIPES[wanted_area][wanted_category]) == dict:
        view.add_item(discord.ui.Button(emoji='⬅', custom_id='arrow_left', row=1))
        view.add_item(discord.ui.Button(emoji='➡', custom_id='arrow_right', row=1))

        embed.description = f"""
**These are the {wanted_category}s you can make in zone {int_to_roman(wanted_area)}:**
{CRAFT_MSG[wanted_category]}
{RECIPES[wanted_area][wanted_category][page]}
**PAGE: {page}/{len(RECIPES[wanted_area][wanted_category])}**"""
    else:
        embed.description = f"""
**These are the {wanted_category}s you can make in zone {int_to_roman(wanted_area)}:**
{CRAFT_MSG[wanted_category]}
{RECIPES[wanted_area][wanted_category]}"""

    view.add_item(select)

    for child in view.children:
        if child.custom_id == f"recipes_{wanted_category}s":
            child.disabled = True
            child.style = discord.ButtonStyle.green

    recipes_embed = await send_response(embed=embed, view=view)

    def check(inter: discord.Interaction):
        return inter.message and inter.message.id == recipes_embed.id

    while True:
        try:
            interaction = await bot.wait_for('interaction', timeout=120, check=check)
        except asyncio.TimeoutError:
            for child in view.children:
                child.disabled = True
            await recipes_embed.edit(view=view)
            return

        if interaction.user.id != author.id:
            await interaction.response.send_message(
                content="This is not your command! Use `val recipes` to browse recipes yourself!", ephemeral=True)
            continue

        embed = discord.Embed(colour=ZONES[wanted_area]['color'])
        embed.set_author(name=f"{author.name}'s recipes", icon_url=author.avatar)
        embed.set_footer(text="Use `val recipes [category] [zone_number]` to check the recipes of other zones!")

        for child in view.children:
            if child.custom_id in (
                    'recipes_pickaxes', 'recipes_items', 'recipes_armors', 'recipes_builds', 'recipes_weapons'):
                child.disabled = False
                child.style = discord.ButtonStyle.grey

        if interaction.data['custom_id'] == 'recipes_pickaxes':
            wanted_category = 'pickaxe'

        elif interaction.data['custom_id'] == 'recipes_items':
            wanted_category = 'item'

        elif interaction.data['custom_id'] == 'recipes_weapons':
            wanted_category = 'weapon'

        elif interaction.data['custom_id'] == 'recipes_armors':
            wanted_category = 'armor'

        elif interaction.data['custom_id'] == 'recipes_builds':
            wanted_category = 'build'

        elif interaction.data['custom_id'] == 'arrow_left':
            page -= 1
            if page not in RECIPES[wanted_area][wanted_category]:
                page = list(RECIPES[wanted_area][wanted_category].keys())[-1]

        elif interaction.data['custom_id'] == 'arrow_right':
            page += 1
            if page not in RECIPES[wanted_area][wanted_category]:
                page = list(RECIPES[wanted_area][wanted_category].keys())[0]

        elif interaction.data['custom_id'] == 'recipes_select':
            wanted_area = int(interaction.data['values'][0])

        for child in view.children:
            if child.custom_id == f"recipes_{wanted_category}s":
                child.disabled = True
                child.style = discord.ButtonStyle.green

        if type(RECIPES[wanted_area][wanted_category]) == dict:
            for child in view.children:
                if child.custom_id in ('arrow_left', 'arrow_right'):
                    break
            else:
                view.add_item(discord.ui.Button(emoji='⬅', custom_id='arrow_left', row=1))
                view.add_item(discord.ui.Button(emoji='➡', custom_id='arrow_right', row=1))

            embed.description = f"""
                **These are the {wanted_category}s you can make in zone {int_to_roman(wanted_area)}:**
{CRAFT_MSG[wanted_category]}
{RECIPES[wanted_area][wanted_category][page]}
**PAGE: {page}/{len(RECIPES[wanted_area][wanted_category])}**"""
        else:
            for child in view.children:
                if child.custom_id in ('arrow_left', 'arrow_right'):
                    view.remove_item(child)

            embed.description = f"""
                            **These are the {wanted_category}s you can make in zone {int_to_roman(wanted_area)}:**
{CRAFT_MSG[wanted_category]}
{RECIPES[wanted_area][wanted_category]}"""

        await interaction.response.edit_message(embed=embed, view=view)


async def val_craft(channel: discord.TextChannel,
                    author: discord.User,
                    command: str,
                    interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=f"<@{author.id}> What are you trying to craft? Correct usage: `val craft [item]`")
            return

        amount = 1

        if parameters[-1].isnumeric():
            amount = int(parameters[-1])
            parameters.pop()

        item_name = ' '.join(parameters)
    else:
        item_name = ' '.join(interaction.data['options'][0]['value'].split())
        if len(interaction.data['options']) > 1:
            amount = interaction.data['options'][1]['value']
        else:
            amount = 1

    if amount <= 0:
        await send_response(content=f"<@{author.id}> The amount must be at least **1**.")
        return

    item_id, item_type = get_it_from_name(item_name)

    if amount > 1 and item_type != 'item':
        await send_response(content=f"<@{author.id}> You can craft only **1** equipment at a time!")
        return

    if item_type in ('station', 'house'):
        await val_build(channel, author, command, interaction=interaction)
        return

    elif item_type == 'pickaxe':
        if is_pickaxe_owned(author.id, item_id):
            await send_response(content=
                                f"<@{author.id}> You **already own** this pickaxe! Equip it using `val equip {PICKAXES[item_id]['name'].lower()}`. "
                                f"Check all available pickaxes using `val equipment`.")
            return

        stations = get_available_crafting_stations_list(author.id)
        station_list = []
        for _, station_id, slot_in_house in stations:
            station_list.append(station_id)

        if PICKAXES[item_id]['station'] not in station_list:
            await send_response(content=
                                f"<@{author.id}> You need a **{CRAFTING_STATIONS[PICKAXES[item_id]['station']]['name']}** to be able to craft this pickaxe! "
                                f"Build it with `val build`")
            return

        await craft(channel, author, PICKAXES[item_id]['recipe'], item_id, item_type, area, interaction=interaction)

    elif item_type == 'armor':
        if is_armor_owned(author.id, item_id):
            await send_response(content=
                                f"<@{author.id}> You **already own** this armor! Equip it using `val equip {ARMORS[item_id]['name'].lower()}`. "
                                f"Check all available armors using `val equipment`.")
            return

        _str, _agi, _end, _int, _luk, _per = get_traits(author.id)
        if _str < ARMORS[item_id]['str']:
            await send_response(content=
                                f"<@{author.id}> You need at least **{ARMORS[item_id]['str']} STR** to equip this armor!")
            return

        stations = get_available_crafting_stations_list(author.id)
        station_list = []
        for _, station_id, slot_in_house in stations:
            station_list.append(station_id)

        if ARMORS[item_id]['station'] not in station_list:
            await send_response(content=
                                f"<@{author.id}> You need a **{CRAFTING_STATIONS[ARMORS[item_id]['station']]['name']}** to be able to craft this armor! "
                                f"Build it with `val build`")
            return

        await craft(channel, author, ARMORS[item_id]['recipe'], item_id, item_type, area, interaction=interaction)

    elif item_type == 'helmet':
        if is_helmet_owned(author.id, item_id):
            await send_response(content=
                                f"<@{author.id}> You **already own** this helmet! Equip it using `val equip {HELMETS[item_id]['name'].lower()}`. "
                                f"Check all available helmets using `val equipment`.")
            return

        _str, _agi, _end, _int, _luk, _per = get_traits(author.id)
        if _str < HELMETS[item_id]['str']:
            await send_response(content=
                                f"<@{author.id}> You need at least **{HELMETS[item_id]['str']} STR** to equip this helmet!")
            return

        stations = get_available_crafting_stations_list(author.id)
        station_list = []
        for _, station_id, slot_in_house in stations:
            station_list.append(station_id)

        if HELMETS[item_id]['station'] not in station_list:
            await send_response(content=
                                f"<@{author.id}> You need a **{CRAFTING_STATIONS[HELMETS[item_id]['station']]['name']}** to be able to craft this helmet! "
                                f"Build it with `val build`")
            return

        await craft(channel, author, HELMETS[item_id]['recipe'], item_id, item_type, area, interaction=interaction)

    elif item_type == 'weapon':
        if is_weapon_owned(author.id, item_id):
            await send_response(content=
                                f"<@{author.id}> You **already own** this weapon! Equip it using `val equip {WEAPONS[item_id]['name'].lower()}`. "
                                f"Check all available weapons using `val equipment`.")
            return

        _str, _agi, _end, _int, _luk, _per = get_traits(author.id)
        if _str < WEAPONS[item_id]['str']:
            await send_response(content=
                                f"<@{author.id}> You need at least **{WEAPONS[item_id]['str']} STR** to wield this weapon!")
            return

        stations = get_available_crafting_stations_list(author.id)
        station_list = []
        for _, station_id, slot_in_house in stations:
            station_list.append(station_id)

        if WEAPONS[item_id]['station'] not in station_list:
            await send_response(content=
                                f"<@{author.id}> You need a **{CRAFTING_STATIONS[WEAPONS[item_id]['station']]['name']}** to be able to craft this weapon! "
                                f"Build it with `val build`")
            return

        await craft(channel, author, WEAPONS[item_id]['recipe'], item_id, item_type, area, interaction=interaction)

    elif item_type == 'item' and 'recipe' in ITEMS[item_id]:
        if 'smelt_time' in ITEMS[item_id]:
            # Has enough items to craft it
            inventory = get_full_inventory_dict(author.id)
            for item_id_recipe, amount_per_item in ITEMS[item_id]['recipe']:
                if item_id_recipe not in inventory or inventory[item_id_recipe] < amount_per_item * amount:
                    await show_items_left_required(channel, author, ITEMS[item_id]['recipe'], inventory, area,
                                                   amount=amount, interaction=interaction)
                    return

            full_furnace_details = get_furnaces_info(author.id)
            if not full_furnace_details:
                await send_response(content=f"<@{author.id}> You don't have a furnace to smelt this in! Make one with `val build`!")
                return

            eligible_furances = []
            for fslot in full_furnace_details:
                if full_furnace_details[fslot]['item_inside'] == item_id or\
                        not full_furnace_details[fslot]['item_inside']:
                    eligible_furances.append(fslot)

            if eligible_furances:
                for furnace in eligible_furances:
                    if full_furnace_details[furnace]['furnace_id'] < ITEMS[item_id]['station']:
                        eligible_furances.remove(furnace)

                if not eligible_furances:
                    await send_response(
                        content=f"<@{author.id}> You need at least a **{CRAFTING_STATIONS[ITEMS[item_id]['station']]['emoji']} "
                                f" {CRAFTING_STATIONS[ITEMS[item_id]['station']]['name']}** to smelt this!")
                    return

            interaction = None
            furnace_to_smelt_slot = -1
            if len(eligible_furances) > 1:
                furnace_to_smelt_slot, interaction = await ask_what_furnace(channel, author, item_id, amount,
                                                                            len(eligible_furances),
                                                                            interaction=interaction)
                if not interaction:
                    return

            elif eligible_furances:
                furnace_to_smelt_slot = eligible_furances[0]

            if furnace_to_smelt_slot == -1:
                await send_response(content=
                                    f"<@{author.id}> You don't have a free furnace! You can remove the items from furnaces in `val house`")
                return


            for item_id_recipe, amount_per_item in ITEMS[item_id]['recipe']:
                remove_item(author.id, item_id_recipe, amount_per_item * amount)

            item_done_amount, item_done_id = format_furnace_view('', full_furnace_details, furnace_to_smelt_slot,
                                                                 author.id,
                                                                 just_give_rewards=True)

            next_item_done = get_left_on_item(author.id, furnace_to_smelt_slot)
            if not next_item_done:
                add_item_in_furnace(author.id, item_id, amount, furnace_to_smelt_slot,
                                    set_time=ITEMS[item_id]['smelt_time'])
            else:
                add_item_in_furnace(author.id, item_id, amount, furnace_to_smelt_slot)

            text = ''
            if item_done_amount:
                text += f"Collected **+{item_done_amount} {ITEMS[item_done_id]['emoji']} {ITEMS[item_done_id]['name']}** from the furnace.\n"

            text += f"Added **{amount} {ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** to smelt in furnace on slot {furnace_to_smelt_slot + 1}.\n" \
                    f"Check the progress in `val house`."
            if interaction:
                await interaction.response.send_message(text)
            else:
                await send_response(content=text)

    else:
        closest_matched = difflib.get_close_matches(item_name, ALL_CRAFTABLES, 5)
        text = ''
        for word in closest_matched:
            if len(closest_matched) > 0 and word == closest_matched[0]:
                text += f'`{word}`'
            elif len(closest_matched) > 1 and word == closest_matched[-1]:
                text += f' or `{word}`'
            else:
                text += f", `{word}`"

        m_text = f"<@{author.id}> What are you trying to craft?\n"
        if closest_matched:
            m_text += f"Did you mean: {text}?"
        else:
            m_text += "Check the name of the item again!"

        m_text += "\nCorrect usage: `val craft [item]`"
        await send_response(content=m_text)


async def craft(channel, author, recipe, craft_id, _type, zone, interaction=None):
    inventory = get_full_inventory_dict(author.id)

    # Check if user has everything required
    for item_id, amount in recipe:
        if item_id not in inventory or inventory[item_id] < amount:
            await show_items_left_required(channel, author, recipe, inventory, zone=zone, amount=1,
                                           interaction=interaction)
            return

    for item_id, amount in recipe:
        remove_item(author.id, item_id, amount)

    if _type == 'pickaxe':
        add_pickaxe(author.id, craft_id)

        embed = discord.Embed(colour=ZONES[zone]['color'])
        embed.set_thumbnail(url=author.avatar)
        embed.set_author(name=f"{author.name}'s {PICKAXES[craft_id]['name'].lower()}", icon_url=author.avatar)
        embed.description = (
                f"✨ **{PICKAXES[craft_id]['emoji']} {PICKAXES[craft_id]['name']} successfully crafted** !✨\n" +
                (f"{PICKAXES[craft_id]['special_text']}" if 'special_text' in PICKAXES[craft_id] else ''))
        embed.set_footer(text="Check [val help <pickaxe>] for more info!")
        emoji = bot.get_emoji(int(PICKAXES[craft_id]['emoji'].split(':')[2][:-1]))
        embed.set_image(url=emoji.url)

        if interaction and interaction.command:
            await interaction.edit_original_response(embed=embed)
        else:
            await channel.send(author.mention, embed=embed)

    if _type == 'armor':
        add_armor(author.id, craft_id)

        embed = discord.Embed(colour=ZONES[zone]['color'])
        embed.set_thumbnail(url=author.avatar)
        embed.set_author(name=f"{author.name}'s {ARMORS[craft_id]['name'].lower()}", icon_url=author.avatar)
        embed.description = (
                f"✨ **{ARMORS[craft_id]['emoji']} {ARMORS[craft_id]['name']} successfully crafted** !✨\n" +
                (f"{ARMORS[craft_id]['special_text']}" if 'special_text' in ARMORS[craft_id] else ''))
        embed.set_footer(text="Check [val help <weapon>] for more info!")
        emoji = bot.get_emoji(int(ARMORS[craft_id]['emoji'].split(':')[2][:-1]))
        embed.set_image(url=emoji.url)

        if interaction and interaction.command:
            await interaction.edit_original_response(embed=embed)
        else:
            await channel.send(author.mention, embed=embed)

    if _type == 'weapon':
        add_weapon(author.id, craft_id)

        embed = discord.Embed(colour=ZONES[zone]['color'])
        embed.set_thumbnail(url=author.avatar)
        embed.set_author(name=f"{author.name}'s {WEAPONS[craft_id]['name'].lower()}", icon_url=author.avatar)
        embed.description = (
                f"✨ **{WEAPONS[craft_id]['emoji']} {WEAPONS[craft_id]['name']} successfully crafted** !✨\n" +
                (f"{WEAPONS[craft_id]['special_text']}" if 'special_text' in WEAPONS[craft_id] else ''))
        embed.set_footer(text="Check [val help <weapon>] for more info!")
        emoji = bot.get_emoji(int(WEAPONS[craft_id]['emoji'].split(':')[2][:-1]))
        embed.set_image(url=emoji.url)

        if interaction and interaction.command:
            await interaction.edit_original_response(embed=embed)
        else:
            await channel.send(author.mention, embed=embed)

    if _type == 'helmet':
        add_helmet(author.id, craft_id)

        embed = discord.Embed(colour=ZONES[zone]['color'])
        embed.set_thumbnail(url=author.avatar)
        embed.set_author(name=f"{author.name}'s {HELMETS[craft_id]['name'].lower()}", icon_url=author.avatar)
        embed.description = (
                f"✨ **{HELMETS[craft_id]['emoji']} {HELMETS[craft_id]['name']} successfully crafted** !✨\n" +
                (f"{HELMETS[craft_id]['special_text']}" if 'special_text' in HELMETS[craft_id] else ''))
        embed.set_footer(text="Check [val help <weapon>] for more info!")
        emoji = bot.get_emoji(int(HELMETS[craft_id]['emoji'].split(':')[2][:-1]))
        embed.set_image(url=emoji.url)

        if interaction and interaction.command:
            await interaction.edit_original_response(embed=embed)
        else:
            await channel.send(author.mention, embed=embed)


async def ask_what_furnace(channel, author, item, amount, furnace_amount, add_fuelm=False, remove_fuelm=False,
                           interaction=None):
    view = discord.ui.View()
    for i in range(1, furnace_amount + 1):
        view.add_item(discord.ui.Button(emoji=get_number_emoji(i), custom_id=str(i - 1)))

    if not remove_fuelm:
        text = f"<@{author.id}> You have more than one furnace,  what is **the slot** of the furnace you want {'to smelt' if not add_fuelm else 'to add'} **{amount} {ITEMS[item]['emoji']} {ITEMS[item]['name']}** in?"
    else:
        text = f"<@{author.id}> You have more than one furnace with fuel inside, what is **the slot** of the furnace you want to remove fuel from?"

    if interaction and interaction.command:
        asking_msg = await interaction.edit_original_response(content=text, view=view)
    else:
        asking_msg = await channel.send(content=text, view=view)

    def check(inter):
        return inter.message.id == asking_msg.id

    while True:
        try:
            interaction = await bot.wait_for('interaction', check=check, timeout=15)
        except asyncio.TimeoutError:
            for button in view.children:
                button.disabled = True
            await asking_msg.edit(view=view)
            await channel.send(f"<@{author.id}> Try choosing the furnace faster next time!")
            return -1, None

        if interaction.user.id != author.id:
            continue

        if interaction.data['custom_id'].isnumeric():
            return int(interaction.data['custom_id']), interaction


async def val_destory(channel, author, command, interaction=None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=f"<@{author.id}> What are you trying to destroy?\n"
                                        f"Correct usage: `val destroy [crafting_station] [slot_in_house]`.")
            return

        slot_number = 0

        if parameters[-1].isnumeric():
            slot_number = int(parameters[-1])
            parameters.pop()

        name = ' '.join(parameters)
    else:
        name = ' '.join(interaction.data['options'][0]['value'].split())
        if len(interaction.data['options']) > 1:
            slot_number = interaction.data['options'][1]['value']
        else:
            slot_number = 0

    build_id, _type = get_it_from_name(name)

    if _type == 'house':
        await send_response(content=f"<@{author.id}> You can't destroy your house!")
        return

    if _type != 'station':
        await send_response(content=f"<@{author.id}> You need to specify a **crafting station** to destroy!"
                                    f" Check `/house` to see your current crafting stations, or `/recipes` -> `builds` to see which ones you can make!")
        return

    if not build_id:
        await send_response(content=f"<@{author.id}> What are you trying to destroy? Check the crafting station name again!")
        return

    station_list = []
    house_slots = {}
    crafting_stations = get_available_crafting_stations_list(author.id)
    for _, station_id, slot_in_house in crafting_stations:
        station_list.append(station_id)
        house_slots[slot_in_house] = station_id

    if build_id not in station_list:
        await send_response(
            content=f"<@{author.id}> You don't have a **{CRAFTING_STATIONS[build_id]['emoji']} {CRAFTING_STATIONS[build_id]['name']}** in your house!")
        return

    if not slot_number and station_list.count(build_id) > 1:
        await send_response(content=
                            f"<@{author.id}> You have more than one **{CRAFTING_STATIONS[build_id]['emoji']} {CRAFTING_STATIONS[build_id]['name']}** in your house!\n"
                            f"Please also specify the slot number in the house with `val destroy {name} [slot]`.")
        return

    if not slot_number:
        for slots in house_slots:
            if house_slots[slots] == build_id:
                delete_station(author.id, build_id, slots)
                await send_response(content=
                                    f"<@{author.id}> Successfully destroyed **{CRAFTING_STATIONS[build_id]['emoji']} {CRAFTING_STATIONS[build_id]['name']}** from slot {slots + 1}")

                return

    elif slot_number:
        slot_number -= 1
        if slot_number not in house_slots:
            await send_response(content=
                                f"<@{author.id}> That slot is already empty or doesn't exist!")
            return

        if house_slots[slot_number] == build_id:
            delete_station(author.id, build_id, slot_number)
            await send_response(content=
                                f"<@{author.id}> Successfully destroyed **{CRAFTING_STATIONS[build_id]['emoji']} {CRAFTING_STATIONS[build_id]['name']}** from slot {slot_number + 1}")

            return
        else:
            await send_response(content=
                                f"<@{author.id}> Slot {slot_number + 1} in your house isn't occupied by a **{CRAFTING_STATIONS[build_id]['emoji']} {CRAFTING_STATIONS[build_id]['name']}**!")
            return


async def val_seek(channel: discord.TextChannel,
                   author: discord.User,
                   interaction: discord.Interaction = None):
    area, max_area, hp, max_hp, trait_points, current_xp, level, mana, max_mana = await get_all_player_info(channel, author)
    if not area:
        return

    cooldown = get_cooldown(author.id, 2)
    if time.time() - cooldown <= 60.0:
        await cooldown_warning(channel, author, 'seek enemies', 60 - int(time.time() - cooldown), area,
                               interaction=interaction)
        return

    pickaxe, weapon, helmet, chest = get_all_player_gear(author.id)
    STR, AGI, END, INT, LUK, PER = get_traits(author.id)

    text = f"""**{author.name}** is {HUNT_PHASES_search[random.randint(0, 6)]} {random.choice(ZONES[area]['emoji'])} **{ZONES[area]['name']}**!\n"""
    # STATFORMULA
    user_defense = HELMETS[helmet]['def'] + ARMORS[chest]['def'] + AGI // 3 + STR // 2 + END
    user_attack = 2 * STR * ('normal' == WEAPONS[weapon]['type']) + int(
        1.5 * AGI * ('light' == WEAPONS[weapon]['type'])) + WEAPONS[weapon]['at']

    enemy_encountered = 0
    item_dropped = 0
    item_amount = 0
    hp_lost = 0
    xp_gained = 0

    if area == 1:
        if level >= 8 and random_float(0, 99) <= 1 + LUK * 0.05:
            enemy_encountered = 1
            hp_lost = random.randint(int(ENEMIES[1]['dmg'] - ENEMIES[1]['dmg'] * 0.3), ENEMIES[1]['dmg'])
            if random_float(1, 100) <= 30:
                item_dropped = 11
                item_amount = 1
            xp_gained = random.randint(300, 500 + level)

        elif level >= 4 and random_float(0, 20) <= 1 + LUK * 0.04:
            enemy_encountered = 2
            hp_lost = random.randint(int(ENEMIES[2]['dmg'] - ENEMIES[2]['dmg'] * 0.3), ENEMIES[2]['dmg'])

            if random_float(1, 100) <= 10:
                item_dropped = 9
                item_amount = 1
            xp_gained = random.randint(90, 110 + level)

        else:
            xp_gained = random.randint(level * 2 + 18, level * 2 + 27)

            enemy_encountered = random.choice((3, 4, 5))
            if enemy_encountered == 3:
                # WOLF
                hp_lost = random.randint(int(ENEMIES[3]['dmg'] - ENEMIES[3]['dmg'] * 0.3), ENEMIES[3]['dmg'])
                xp_gained -= 5
                if random_float(1, 100) <= 10 + LUK * 0.05:
                    item_dropped = 7
                    item_amount = 1

            elif enemy_encountered == 4:
                hp_lost = random.randint(int(ENEMIES[4]['dmg'] - ENEMIES[4]['dmg'] * 0.3), ENEMIES[4]['dmg'])
                xp_gained += 15

            elif enemy_encountered == 5:
                # SLIME
                hp_lost = random.randint(int(ENEMIES[5]['dmg'] - ENEMIES[5]['dmg'] * 0.3), ENEMIES[5]['dmg'])
                xp_gained -= 10

                if random_float(1, 100) <= 10 + LUK * 0.05:
                    item_dropped = 8
                    item_amount = 1

    elif area == 2:
        if level >= 14 and random_float(0, 20) <= 1 + LUK * 0.04:
            enemy_encountered = 9
            xp_gained = random.randint(250, 500 + level)

        else:
            xp_gained = random.randint(level * 2 + 200, level * 2 + 260)

            enemy_encountered = random.choice((6, 7, 8))
            if enemy_encountered == 6:
                xp_gained -= 50

            elif enemy_encountered == 7:
                if random_float(1, 100) <= 10 + LUK * 0.05:
                    item_dropped = 23
                    item_amount = 1
                xp_gained += 50

            elif enemy_encountered == 8:
                if random_float(1, 100) <= 40 + LUK * 0.05:
                    item_dropped = 21
                    item_amount = random.randint(1, 3)

        hp_lost = random.randint(ENEMIES[enemy_encountered]['min_dmg'], ENEMIES[enemy_encountered]['max_dmg'])

    int_xp_extra = int(math.ceil(xp_gained * (INT / 200)))
    xp_gained += int_xp_extra if int_xp_extra < (level + INT) * 2 else (level + INT) * 2

    has_dodged = random.randint(1, ENEMIES[enemy_encountered]['dodgeAGI']) <= AGI
    if AGI >= ENEMIES[enemy_encountered]['dodgeAGI'] * 0.7:
        if random.randint(1, 100) <= 70:
            has_dodged = False

    if not has_dodged:
        hp_lost -= (user_defense + user_attack)
        if hp_lost < 0:
            hp_lost = 0

        hp -= hp_lost
    else:
        hp_lost = 0

    if hp > 0:
        text += f"""**{author.name}** {random.choice(HUNT_PHASES_found)} and {random.choice(HUNT_PHASES_kill)} a {ENEMIES[enemy_encountered]['emoji']} **{ENEMIES[enemy_encountered]['name']}**!\n"""

        if has_dodged:
            text += f"""**{author.name}** was fast enough and dodged the **{ENEMIES[enemy_encountered]['name']}'s** attack! **You** gained +{xp_gained}XP\n"""
        else:
            text += f"""The **{ENEMIES[enemy_encountered]['name']}** did {hp_lost} damage and left you with {hp}/{max_hp} HP. **You** gained +{xp_gained}XP\n"""

        if item_dropped:
            text += f"""The **{ENEMIES[enemy_encountered]['name']}** dropped {item_amount} **{ITEMS[item_dropped]['emoji']} {ITEMS[item_dropped]['name']}**!\n"""
            add_item(author.id, item_dropped, item_amount)

        if xp_gained + current_xp >= NEXT_XP[level]:
            text += level_up_message(author, xp_gained + current_xp - NEXT_XP[level], level)
        else:
            add_xp(author.id, xp_gained)

    if hp <= 0:
        set_hp(author.id, 1)
        text += f"""**{author.name}** {random.choice(HUNT_PHASES_found)} a {ENEMIES[enemy_encountered]['emoji']} **{ENEMIES[enemy_encountered]['name']}**!\n"""
        text += f"""The **{ENEMIES[enemy_encountered]['name']}** did {hp_lost} damage and {random.choice(HUNT_PHASES_kill)} **{author.name}**!\n"""
        text += f"""**{author.name}** died!"""

    elif hp_lost:
        set_hp(author.id, hp)

    update_cooldown(author.id, 2)

    heal_button = discord.ui.View()
    if hp != max_hp:
        heal_button.add_item(discord.ui.Button(label='Heal', emoji=EMOJIS['heal'], custom_id='heal_command'))

    if interaction and interaction.command:
        await interaction.edit_original_response(content=text, view=heal_button)
    else:
        await channel.send(text, view=heal_button)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Seek again", emoji=ENEMIES[enemy_encountered]['emoji'],
                                    style=discord.ButtonStyle.blurple, custom_id='seek_command'))
    return view


async def val_heal(channel: discord.TextChannel,
                   author: discord.User,
                   command: str,
                   interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if not interaction:
        parameters = command.split()[2:]
    else:
        parameters = []
        if 'options' in interaction.data and interaction.data['options'][0]['value']:
            parameters.append('full')

    hp, max_hp = get_current_hp(author.id)

    if hp == max_hp:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f'HP: {hp}/{max_hp}', emoji=EMOJIS['hp'], disabled=True))

        if interaction and interaction.command:
            await interaction.edit_original_response(content=f"**{author.name}**, your health is already **full**!",
                                                     view=view)
            return

        await channel.send(f"**{author.name}**, your health is already **full**!", view=view)
        return

    overheal = False
    if parameters:
        if parameters[-1] == 'full':
            overheal = True

    possible_healing_items = []

    inventory = get_full_inventory_dict(author.id)

    for item in inventory:
        if inventory[item] and 'heal_power' in ITEMS[item]:
            possible_healing_items.append(item)

    if not possible_healing_items:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f'HP: {hp}/{max_hp}', emoji=EMOJIS['hp'], disabled=True))

        if interaction:
            await channel.send(content=
                                                     f"**{author.name}** You don't have any items to heal yourself! Check `val help heal` to learn what items can heal you!",
                                                     view=view)
            return

        await channel.send(
            f"**{author.name}** You don't have any items to heal yourself! Check `val help heal` to learn what items can heal you!",
            view=view)
        return

    text = ''
    possible_healing_items = sorted(possible_healing_items, key=lambda x: ITEMS[x]['heal_power'])

    items_consumed = []
    to_heal = max_hp - hp
    if not overheal:
        for item in possible_healing_items:
            if to_heal <= 0:
                break

            amount = to_heal // ITEMS[item]['heal_power']
            if amount > inventory[item]:
                amount = inventory[item]

            if not amount:
                continue

            to_heal -= ITEMS[item]['heal_power'] * amount
            items_consumed.append([item, amount])

        # So it doesn't use 5 items with 30HP, and then another items for 150 that heals to full anyway
        for i in range(len(items_consumed)):
            if to_heal >= 0:
                break
            can_remove = abs(to_heal) // ITEMS[items_consumed[i][0]]['heal_power']
            if not can_remove:
                break
            to_heal += items_consumed[i][1] * ITEMS[items_consumed[i][0]]['heal_power']
            if to_heal >= 0:
                to_heal = 0

            items_consumed[i][1] -= can_remove
            if items_consumed[i][1] < 0:
                items_consumed[i][1] = 0

        if not items_consumed:
            # await reply(
            #     f"**You** can't consume any items without going over the max HP. Consider using `val heal full` instead! "
            #     f"Check `val help heal` for more info.")
            items_consumed.append([possible_healing_items[0], 1])

        text = f"**{author.name}** consumed "
        for item, amount in items_consumed:
            inventory[item] -= amount
            if amount:
                text += f"**{amount} {ITEMS[item]['emoji']} {ITEMS[item]['name']}**, "
        total_healed = sum([ITEMS[i]['heal_power'] * amount for i, amount in items_consumed])

        if total_healed + hp > max_hp:
            total_healed = max_hp - hp
        hp += total_healed

        text += f"and replenished **{total_healed} HP!**" \
                f" Now you have **{hp}/{max_hp} HP**!"

        for item, amount in items_consumed:
            remove_item(author.id, item, amount)

        set_hp(author.id, hp)

    elif overheal:
        for item in possible_healing_items:
            if to_heal <= 0:
                break

            amount = math.ceil(to_heal / ITEMS[item]['heal_power'])

            if not amount:
                continue

            if amount > inventory[item]:
                amount = inventory[item]

            to_heal -= ITEMS[item]['heal_power'] * amount
            items_consumed.append([item, amount])

        # So it doesn't use 5 items with 30HP, and then another items for 150 that heals to full anyway
        for i in range(len(items_consumed)):
            if to_heal >= 0:
                break
            can_remove = abs(to_heal) // ITEMS[items_consumed[i][0]]['heal_power']
            if not can_remove:
                break
            to_heal += items_consumed[i][1] * ITEMS[items_consumed[i][0]]['heal_power']
            if to_heal >= 0:
                to_heal = 0

            items_consumed[i][1] -= can_remove
            if items_consumed[i][1] < 0:
                items_consumed[i][1] = 0

        text = f"**{author.name}** consumed "
        for item, amount in items_consumed:
            inventory[item] -= amount
            if amount:
                text += f"**{amount} {ITEMS[item]['emoji']} {ITEMS[item]['name']}**, "

        total_healed = sum([ITEMS[i]['heal_power'] * amount for i, amount in items_consumed])

        if total_healed + hp > max_hp:
            total_healed = max_hp - hp
        hp += total_healed

        text += f"and replenished **{total_healed} HP!**" \
                f" Now you have **{hp}/{max_hp} HP**!"

        for item, amount in items_consumed:
            remove_item(author.id, item, amount)

        set_hp(author.id, hp)

    heal_full_view = discord.ui.View()
    if not overheal and hp < max_hp:
        possible_healing_items = []
        for item in inventory:
            if inventory[item] and 'heal_power' in ITEMS[item]:
                possible_healing_items.append(item)

        if not possible_healing_items:
            heal_full_view.add_item(
                discord.ui.Button(label='No healing items left', emoji=EMOJIS['heal'], disabled=True))
        else:
            heal_full_view.add_item(
                discord.ui.Button(label='Heal full', emoji=EMOJIS['heal'], custom_id='heal_command'))

    if interaction and interaction.command:
        await interaction.edit_original_response(content=text, view=heal_full_view)
    else:
        await channel.send(text, view=heal_full_view)


async def val_traits(channel: discord.TextChannel,
                     author: discord.User,
                     interaction_command=None,
                     assign_screen=False,
                     slash_command: discord.Interaction = None):
    stats = await get_all_player_info(channel, author)
    if not stats:
        return

    area, max_area, hp, max_hp, trait_points, _, level, mana, max_mana = stats
    STR, AGI, END, INT, LUK, PER = get_traits(author.id)
    remove_multiplier = 5

    max_trait_points = trait_points
    tspend_message = None
    view = None
    interaction = None
    msg = None
    values_to_add = []
    event_name = ''
    spend_amounts = [0 for i in range(6)]
    amount = 1
    embed = discord.Embed(color=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s traits", icon_url=author.avatar)
    embed.set_footer(text='Use [val help traits] to learn more')
    tspend_message_content = ''

    remove_screen = False
    remove_waring_screen = False
    start_screen = True if not assign_screen else False
    benefits_screen = False
    check_i = None
    while True:
        if tspend_message:
            if not check_i:
                DATA_CACHE[author.id]['traits_message_id'] = tspend_message.id

                def check_i(inter):
                    return inter.message and inter.message.id == tspend_message.id

            def check_m(msg):
                return msg.author.id == author.id and msg.channel.id == channel.id \
                       and msg.content.replace(f'<@{bot.user.id}>', '').replace(f'-', '').strip().isnumeric()

            tasks = [asyncio.create_task(bot.wait_for('interaction', check=check_i), name='interaction'),
                     asyncio.create_task(bot.wait_for('message', check=check_m), name='message')]

            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED, timeout=120)

            for task in pending:
                task.cancel()

            if len(pending) == 2:
                for child in view.children:
                    child.disabled = True
                await tspend_message.edit(view=view)
                return

            for event in done:
                event_name = event.get_name()
                if event_name == 'interaction':
                    interaction = event.result()
                else:
                    msg = event.result()

            if not (assign_screen or remove_screen) and event_name == 'message':
                continue

            if event_name == 'interaction':
                if interaction.message.id != DATA_CACHE[author.id]['traits_message_id']:
                    for child in view.children:
                        child.disabled = True

                    await interaction.response.edit_message(view=view)
                    return

                if interaction.user.id != author.id:
                    await interaction.response.send_message(
                        content="This is not your command! Use `val traits` to do it yourself!", ephemeral=True)
                    continue

                elif interaction.data['custom_id'] == 'cancel_traits':
                    values_to_add = []
                    spend_amounts = [0 for i in range(6)]
                    amount = 1
                    start_screen = True
                    remove_screen = False
                    assign_screen = False

                elif interaction.data['custom_id'] == 'str_add':
                    spend_amounts[0] += amount

                elif interaction.data['custom_id'] == 'agi_add':
                    spend_amounts[1] += amount

                elif interaction.data['custom_id'] == 'end_add':
                    spend_amounts[2] += amount

                elif interaction.data['custom_id'] == 'int_add':
                    spend_amounts[3] += amount

                elif interaction.data['custom_id'] == 'luk_add':
                    spend_amounts[4] += amount

                elif interaction.data['custom_id'] == 'per_add':
                    spend_amounts[5] += amount

                elif interaction.data['custom_id'] == 'done_add':
                    STR += spend_amounts[0]
                    AGI += spend_amounts[1]
                    END += spend_amounts[2]
                    INT += spend_amounts[3]
                    LUK += spend_amounts[4]
                    PER += spend_amounts[5]
                    values_to_add = copy.deepcopy(spend_amounts)
                    spend_amounts = [0 for i in range(6)]
                    assign_screen = False
                    start_screen = True
                    max_trait_points -= sum(values_to_add)

                # Remove Screen
                elif interaction.data['custom_id'] == 'done_rem':
                    total_removed = sum([-i for i in spend_amounts])
                    if total_removed % remove_multiplier:
                        await interaction.response.send_message(f"""<@{interaction.user.id}>, the points removed must a \
multiple of **{remove_multiplier}** (the same amount you gain when you level up).
Please remove **{round_to_multiple(total_removed, remove_multiplier) - total_removed} more points**, or add back **{total_removed - (round_to_multiple(total_removed, remove_multiplier) - remove_multiplier)} points**.""")
                        continue

                    STR += spend_amounts[0]
                    AGI += spend_amounts[1]
                    END += spend_amounts[2]
                    INT += spend_amounts[3]
                    LUK += spend_amounts[4]
                    PER += spend_amounts[5]
                    values_to_add = copy.deepcopy(spend_amounts)
                    spend_amounts = [0 for i in range(6)]
                    remove_screen = False
                    start_screen = True

                elif interaction.data['custom_id'] == 'str_rem':
                    spend_amounts[0] += amount

                elif interaction.data['custom_id'] == 'agi_rem':
                    spend_amounts[1] += amount

                elif interaction.data['custom_id'] == 'end_rem':
                    spend_amounts[2] += amount

                elif interaction.data['custom_id'] == 'int_rem':
                    spend_amounts[3] += amount

                elif interaction.data['custom_id'] == 'luk_rem':
                    spend_amounts[4] += amount

                elif interaction.data['custom_id'] == 'per_rem':
                    spend_amounts[5] += amount

                elif interaction.data['custom_id'] == 'view_benefits':
                    benefits_screen = True

                # Choosing action:
                elif interaction.data['custom_id'] == 'assign_points':
                    assign_screen = True
                    start_screen = False

                elif interaction.data['custom_id'] == 'remove_points':
                    remove_waring_screen = True
                    start_screen = False

                elif interaction.data['custom_id'] == 'close_tspend':
                    for child in view.children:
                        child.disabled = True

                    await interaction.response.edit_message(view=view)
                    return

                # Warning screen
                elif interaction.data['custom_id'] == 'warning_no':
                    embed = discord.Embed(color=ZONES[area]['color'])
                    embed.set_author(name=f"{author.name}'s traits", icon_url=author.avatar)
                    embed.set_footer(text='Use [val help traits] to learn more')
                    tspend_message_content = ''
                    start_screen = True
                    remove_waring_screen = False

                elif interaction.data['custom_id'] == 'warning_yes':
                    embed = discord.Embed(color=ZONES[area]['color'])
                    embed.set_author(name=f"{author.name}'s traits", icon_url=author.avatar)
                    embed.set_footer(text='Use [val help traits] to learn more')
                    tspend_message_content = ''
                    remove_waring_screen = False
                    remove_screen = True
                    amount = -1

            else:
                content = msg.content.replace(f'<@{bot.user.id}>', '').strip()
                if not content:
                    continue
                if content[0] == '-' and content.count('-') == 1:
                    amount = -int(content.replace('-', ''))

                    if assign_screen:
                        if amount < -max_trait_points:
                            amount = -max_trait_points
                    elif remove_screen:
                        if -amount > max([STR, AGI, END, INT, LUK, PER]):
                            amount = -max([STR, AGI, END, INT, LUK, PER])

                elif content.isnumeric():
                    amount = int(content)
                    # print(amount, )
                    if assign_screen:
                        if amount > max_trait_points:
                            amount = max_trait_points

                    if remove_screen:
                        if amount > max([-i for i in spend_amounts]):
                            amount = max([-i for i in spend_amounts])
                else:
                    continue

                if amount == 0:
                    if assign_screen:
                        amount = 1
                    if remove_screen:
                        amount = -1
                try:
                    await msg.delete()
                except discord.HTTPException:
                    pass

        if assign_screen:
            for i, skill in enumerate(spend_amounts):
                if skill < 0:
                    spend_amounts[i] = 0

        if remove_screen:
            for i, skill, tmax in zip(range(6), spend_amounts, [STR, AGI, END, INT, LUK, PER]):
                if -skill > tmax:
                    spend_amounts[i] = -tmax
                if skill > 0:
                    spend_amounts[i] = 0
        if benefits_screen:
            benefits = {'str': "ᐉ no benefits" if not STR + spend_amounts[0] else
            f"""ᐉ +{(STR + spend_amounts[0]) * 2} damage with normal and heavy weapons
ᐉ +{(STR + spend_amounts[0]) // 3} HP
ᐉ +{(STR + spend_amounts[0]) // 2} defense""",

                        'agi': "ᐉ no benefits" if not AGI + spend_amounts[1] else
                        f"""ᐉ +{int((AGI + spend_amounts[1]) * 1.5)} damage with light weapons
ᐉ +{(AGI + spend_amounts[1]) * 0.5:.2f}% chance to dodge attacks in battle
ᐉ +{(AGI + spend_amounts[1]) * 0.01:.2f}% critical hit chance
ᐉ +{(AGI + spend_amounts[1]) // 3} defense""",

                        'end': "ᐉ no benefits" if not END + spend_amounts[2] else
                        f"""ᐉ +{(END + spend_amounts[2]) * 3} HP
ᐉ +{(END + spend_amounts[2])} defense""",

                        'int': "ᐉ no benefits" if not INT + spend_amounts[3] else
                        f"""ᐉ +{(INT + spend_amounts[3])} mana
ᐉ +{(INT + spend_amounts[3]) * 0.5:.2f}% more XP in all commands
ᐉ use `val help [magic weapon]` to see the increase in damage""",

                        'luk': "ᐉ no benefits" if not LUK + spend_amounts[4] else
                        f"""ᐉ +{(LUK + spend_amounts[4]) * 0.08:.2f}% critical hit chance
ᐉ increases luck differently in all commands""",

                        'per': "ᐉ no benefits" if not PER + spend_amounts[5] else
                        f"""ᐉ +{(PER + spend_amounts[5]) // 3} mana"""}

            embed.description = f"""
These are the benefits gained from your traits:
Use `val help traits` to see more info about each trait

💪🏽 **{STR} Strength [STR]:** {f'**+{spend_amounts[0]}**' if spend_amounts[0] else ''}
{benefits['str']}
  
💨 **{AGI} Agility [AGI]:** {f'**+{spend_amounts[1]}**' if spend_amounts[1] else ''}
{benefits['agi']}

💔 **{END} Endurance [END]:** {f'**+{spend_amounts[2]}**' if spend_amounts[2] else ''}
{benefits['end']}

🧠 **{INT} Intellect [INT]:** {f'**+{spend_amounts[3]}**' if spend_amounts[3] else ''}
{benefits['int']}

🍀 **{LUK} Luck [LUK]:** {f'**+{spend_amounts[4]}**' if spend_amounts[4] else ''}
{benefits['luk']}

🗣 **{PER} Personality [PER]** {f'**+{spend_amounts[5]}**' if spend_amounts[5] else ''}
{benefits['per']}

"""

        else:
            embed.description = f"""
This is where you spend your trait points.
Once you assigned a trait point, it can't be undone!
Check `val help traits` to learn more about what each trait does!

**These are your current traits:**
**STR:** {STR if not spend_amounts[0] else f"**{STR} {'+' if spend_amounts[0] > 0 else ''}{spend_amounts[0]}**"}
**AGI:** {AGI if not spend_amounts[1] else f"**{AGI} {'+' if spend_amounts[1] > 0 else ''}{spend_amounts[1]}**"}
**END:** {END if not spend_amounts[2] else f"**{END} {'+' if spend_amounts[2] > 0 else ''}{spend_amounts[2]}**"}
**INT:** {INT if not spend_amounts[3] else f"**{INT} {'+' if spend_amounts[3] > 0 else ''}{spend_amounts[3]}**"}
**LUK:** {LUK if not spend_amounts[4] else f"**{LUK} {'+' if spend_amounts[4] > 0 else ''}{spend_amounts[4]}**"}
**PER:** {PER if not spend_amounts[5] else f"**{PER} {'+' if spend_amounts[5] > 0 else ''}{spend_amounts[5]}**"}

"""
        if start_screen or assign_screen:
            embed.description += f"""{EMOJIS['trait']} **Available trait points:** {trait_points - sum(spend_amounts) - sum(values_to_add)}"""
        if remove_screen:
            embed.description += f"""{EMOJIS['trait']} **Removed trait points:** {trait_points - sum(spend_amounts) - sum(values_to_add)}"""

        if assign_screen or remove_screen:
            embed.description += f"""
ℹ Say a number in chat to change the assign values!
Say a negative number to decrease the points used.
"""
        if amount + sum(spend_amounts) > max_trait_points:
            amount = max_trait_points - sum(spend_amounts)

        # For adding points ====================================================================================
        view = discord.ui.View()
        if assign_screen:
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} STR", custom_id='str_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} AGI", custom_id='agi_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} END", custom_id='end_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} INT", custom_id='int_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} LUK", custom_id='luk_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} PER", custom_id='per_add',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))

            view.add_item(
                discord.ui.Button(label=f'Save', emoji='💾', custom_id='done_add', style=discord.ButtonStyle.blurple,
                                  row=2))
            view.add_item(discord.ui.Button(label=f'Cancel', emoji='✖', custom_id='cancel_traits',
                                            style=discord.ButtonStyle.blurple, row=2))

            if not values_to_add and trait_points - sum(spend_amounts) <= 0 <= amount:
                for child in view.children:
                    if child.custom_id not in ("done_add", 'cancel_traits'):
                        child.disabled = True

            if not values_to_add and amount < 0:
                for child in view.children:
                    if child.custom_id == 'str_add' and spend_amounts[0] <= 0:
                        child.disabled = True
                    if child.custom_id == 'agi_add' and spend_amounts[1] <= 0:
                        child.disabled = True
                    if child.custom_id == 'end_add' and spend_amounts[2] <= 0:
                        child.disabled = True
                    if child.custom_id == 'int_add' and spend_amounts[3] <= 0:
                        child.disabled = True
                    if child.custom_id == 'luk_add' and spend_amounts[4] <= 0:
                        child.disabled = True
                    if child.custom_id == 'per_add' and spend_amounts[5] <= 0:
                        child.disabled = True

        if remove_screen:
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} STR", custom_id='str_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} AGI", custom_id='agi_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} END", custom_id='end_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=0))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} INT", custom_id='int_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} LUK", custom_id='luk_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))
            view.add_item(discord.ui.Button(label=f"{'+' if amount > 0 else ''}{amount} PER", custom_id='per_rem',
                                            style=discord.ButtonStyle.green if amount > 0 else discord.ButtonStyle.red,
                                            row=1))

            view.add_item(
                discord.ui.Button(label=f'Save', emoji='💾', custom_id='done_rem', style=discord.ButtonStyle.blurple,
                                  row=2))
            view.add_item(discord.ui.Button(label=f'Cancel', emoji='✖', custom_id='cancel_traits',
                                            style=discord.ButtonStyle.blurple, row=2))

            if amount < 0:
                for child in view.children:
                    if child.custom_id == 'str_rem' and -spend_amounts[0] >= STR:
                        child.disabled = True
                    if child.custom_id == 'agi_rem' and -spend_amounts[1] >= AGI:
                        child.disabled = True
                    if child.custom_id == 'end_rem' and -spend_amounts[2] >= END:
                        child.disabled = True
                    if child.custom_id == 'int_rem' and -spend_amounts[3] >= INT:
                        child.disabled = True
                    if child.custom_id == 'luk_rem' and -spend_amounts[4] >= LUK:
                        child.disabled = True
                    if child.custom_id == 'per_rem' and -spend_amounts[5] >= PER:
                        child.disabled = True
            elif amount > 0:
                for child in view.children:
                    if child.custom_id == 'str_rem' and spend_amounts[0] >= 0:
                        child.disabled = True
                    if child.custom_id == 'agi_rem' and spend_amounts[1] >= 0:
                        child.disabled = True
                    if child.custom_id == 'end_rem' and spend_amounts[2] >= 0:
                        child.disabled = True
                    if child.custom_id == 'int_rem' and spend_amounts[3] >= 0:
                        child.disabled = True
                    if child.custom_id == 'luk_rem' and spend_amounts[4] >= 0:
                        child.disabled = True
                    if child.custom_id == 'per_rem' and spend_amounts[5] >= 0:
                        child.disabled = True
            else:
                for child in view.children:
                    if child.custom_id not in ("done_rem", 'cancel_traits'):
                        child.disabled = True

        # For picking action ====================================================================================
        if start_screen:
            view.add_item(discord.ui.Button(label='Assign Points', emoji='➕', custom_id='assign_points',
                                            disabled=True if not max_trait_points else False,
                                            style=discord.ButtonStyle.green))
            view.add_item(discord.ui.Button(label='Remove Points', emoji='✖', custom_id='remove_points',
                                            disabled=True if level == 1 else False,
                                            style=discord.ButtonStyle.red))
            view.add_item(
                discord.ui.Button(label='View Benefits', emoji=random.choice("💪💨🍀🧠🗣💔"), custom_id='view_benefits',
                                  style=discord.ButtonStyle.green))

            view.add_item(discord.ui.Button(label='Close', emoji='❕', custom_id='close_tspend',
                                            style=discord.ButtonStyle.red))

        if remove_waring_screen:
            embed = None
            view.add_item(discord.ui.Button(label='Yes', custom_id='warning_yes', style=discord.ButtonStyle.green))
            view.add_item(discord.ui.Button(label='Cancel', custom_id='warning_no', style=discord.ButtonStyle.red))
            tspend_message_content = f"""<@{author.id}>, you will lose **1 level** for every **5 trait points** \
removed. Additionally you will also lose **all the XP gained so far for the next level**.
Are you sure you want to continue?"""

        if not tspend_message:
            if interaction_command:
                # So it removes the button on the profile for ASSIGN TRAITS
                await slash_command.message.edit(view=None)

            if slash_command and slash_command.command:
                tspend_message = await slash_command.edit_original_response(embed=embed, view=view)
            else:
                tspend_message = await channel.send(embed=embed, view=view)
        else:
            if event_name == 'interaction':
                if interaction.data['custom_id'] == 'done_add':
                    if any(values_to_add):
                        update_traits(author.id, values_to_add,
                                      STR - values_to_add[0],
                                      PER - values_to_add[5],
                                      INT - values_to_add[3])
                        add_trait_points(author.id, -sum(values_to_add))

                        await channel.send(f"**{author.name}** has been empowered! Traits increased!")
                        area, max_area, hp, max_hp, trait_points, _, level, mana, max_mana = await get_all_player_info(channel,
                                                                                                                author)
                        STR, AGI, END, INT, LUK, PER = get_traits(author.id)
                        max_trait_points = trait_points
                        values_to_add = []
                        event_name = ''
                        spend_amounts = [0 for i in range(6)]
                        amount = 1

                if interaction.data['custom_id'] == 'done_rem':
                    if any(values_to_add):
                        update_remove_traits(author.id, values_to_add, INT - values_to_add[3], PER - values_to_add[5])
                        levels_to_remove = -sum(values_to_add) // remove_multiplier
                        if levels_to_remove > level - 1:
                            levels_to_remove = level - 1

                        level_down_zero(author.id, levels_to_remove)

                        area, max_area, hp, max_hp, trait_points, _, level, mana, max_mana = await get_all_player_info(channel,
                                                                                                                author)
                        STR, AGI, END, INT, LUK, PER = get_traits(author.id)

                        # Remove equipment because it's too heavy!
                        unequiped = False
                        if values_to_add[0]:
                            pickaxe, weapon, helmet, chest = get_all_player_gear(author.id)
                            if WEAPONS[weapon]['str'] > STR:
                                equip_weapon(author.id, 0)
                                unequiped = True

                            if HELMETS[helmet]['str'] > STR:
                                equip_helmet(author.id, 0)
                                unequiped = True

                            if ARMORS[chest]['str'] > STR:
                                equip_armor(author.id, 0)
                                unequiped = True

                        text = f"**{author.name}** lost his memory... level and traits lowered..."

                        if unequiped:
                            text += f"\n`WARNING:` you unequipped some of your gear because it was too heavy for you!"

                        await channel.send(text)

                        max_trait_points = trait_points
                        values_to_add = []
                        event_name = ''
                        spend_amounts = [0 for i in range(6)]
                        amount = 1

                await interaction.response.edit_message(embed=embed, view=view, content=tspend_message_content)
            else:
                await tspend_message.edit(embed=embed, view=view)


async def val_nc(message, command):
    parameters = [i for i in command.split(' ') if i][2:]

    if len(parameters) < 4:
        await send_val_nc_warn("Not enough parameters.", message)
        return

    for param in parameters[1:]:
        try:
            int(param)
        except (TypeError, ValueError):
            await send_val_nc_warn("USER_ID, ITEM_ID and AMOUNT must be numbers", message)
            return

    category = parameters[0]
    player = int(parameters[1])
    item = int(parameters[2])
    amount = int(parameters[3])

    if amount > 1000 and message.author.id != NECROMANCER_ID:
        await message.channel.send("**MAX AMOUNT = 1000** Please don't use this to get overpowered!")
        return

    if category == 'item' and item not in ITEMS:
        await send_val_nc_warn("Unknown item ID", message)
        return

    if player != message.author.id and message.author.id != NECROMANCER_ID:
        await message.channel.send("You can do changes only on yourself.")
        return

    if category == 'printcache':
        print(DATA_CACHE)

    if category == 'item':
        add_item(player, item, amount)
        await message.channel.send("DONE")

    if category == 'allitem':
        for item in ITEMS:
            add_item(player, item, 1000)

        await message.channel.send("DONE")

    if category == 'trait':
        add_trait_points(player, amount)
        await message.channel.send("DONE")

    if category == 'hp':
        set_hp(player, amount)
        await message.channel.send("DONE")

    if category == 'weapon':
        add_weapon(message.author.id, item)
        await message.channel.send("DONE")

    if category == 'cd':
        update_cooldown_set(player, item, amount)
        await message.channel.send("DONE")

    if category == 'level':
        for i in range(amount):
            level_up(player, i, 0)
        await message.channel.send("DONE")

    if category == 'crate':
        add_crates(player, item, amount)
        await message.channel.send("DONE")

    if category == 'house':
        set_house(player, item)
        await message.channel.send("SET HOUSE DONE")


async def send_val_nc_warn(reason, message):
    await message.channel.send(f":warning: {reason}\nCorrect usage: `val nc [category] [player_id] [item_id] [amount]`."
                               "All fields are required! If a category like `trait` doesnt require item_id, just put `0` there!"
                               "Check pinned messages in `<#1015153868096667658> for the item IDs and categories.")
    return


async def val_cooldown(channel: discord.TextChannel,
                       author: discord.User,
                       command: str,
                       interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    cooldowns = {command_id: time_l for time_l, command_id in get_all_cds(author.id)}

    for i in COMMANDS_WITH_COOLDOWN:
        if i not in cooldowns:
            cooldowns[i] = 0

    embed = discord.Embed(color=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s cooldowns", icon_url=author.avatar)
    embed.set_footer(text="View only the ready to use commands with [val rd]")

    current_time = int(time.time())
    mine_cd = get_pretty_time(int(20 - (current_time - cooldowns[1])))
    seek_cd = get_pretty_time(int(60 - (current_time - cooldowns[2])))
    battle_cd = get_pretty_time(int(3600 - (current_time - cooldowns[3])))
    progress_cd = get_pretty_time(int(28800 - (current_time - cooldowns[20])))

    embed.description = f"""
**Your commands will be ready in:**

⛏ **MINE** — **{'ready' if mine_cd == '0s' else mine_cd}** {'✅' if mine_cd == '0s' else '<:red_x_mark:1019881615155003402>'}
{random.choice(ZONES[area]['emoji'])} **SEEK** — **{'ready' if seek_cd == '0s' else seek_cd}** {'✅' if seek_cd == '0s' else '<:red_x_mark:1019881615155003402>'}
⚔ **BATTLE** — **{'ready' if battle_cd == '0s' else battle_cd}** {'✅' if battle_cd == '0s' else '<:red_x_mark:1019881615155003402>'}
✨ **PROGRESS** — **{'ready' if progress_cd == '0s' else progress_cd}** {'✅' if progress_cd == '0s' else '<:red_x_mark:1019881615155003402>'}
"""
    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(embed=embed)


async def val_ready(channel: discord.TextChannel,
                    author: discord.User,
                    command: str,
                    interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    cooldowns = {command_id: time_l for time_l, command_id in get_all_cds(author.id)}

    for i in COMMANDS_WITH_COOLDOWN:
        if i not in cooldowns:
            cooldowns[i] = 0

    embed = discord.Embed(color=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s cooldowns", icon_url=author.avatar)
    embed.set_footer(text="View all cooldowns with [val cd]")

    current_time = int(time.time())
    mine_cd = get_pretty_time(int(20 - (current_time - cooldowns[1])))
    seek_cd = get_pretty_time(int(60 - (current_time - cooldowns[2])))
    battle_cd = get_pretty_time(int(3600 - (current_time - cooldowns[3])))
    progress_cd = get_pretty_time(int(28800 - (current_time - cooldowns[20])))

    embed.description = f"""
**Your ready to use commands are:**\n
"""
    if mine_cd == '0s':
        embed.description += f"""⛏ **MINE** — **ready** ✅\n"""

    if seek_cd == '0s':
        embed.description += f"""{random.choice(ZONES[area]['emoji'])} **SEEK** — **ready** ✅\n"""

    if battle_cd == '0s':
        embed.description += f"""⚔ **BATTLE** — **ready** ✅\n"""

    if progress_cd == '0s':
        embed.description += f"""✨ **PROGRESS** — **ready** ✅\n"""

    if embed.description == f"""
**Your ready to use commands are:**\n
""":
        embed.description += "__All commands are on cooldown__ <:red_x_mark:1019881615155003402>"

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(embed=embed)


async def val_use(channel: discord.TextChannel,
                  author: discord.User,
                  command: str,
                  interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        amount = 1
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=
                                f"<@{author.id}> What are you trying to use? Check your inventory again to see it's name. Correct usage `val use [item name] [amount]`.")
            return

        if parameters[-1].isnumeric():
            amount = int(parameters[-1])
            parameters.pop()

        item_name = ' '.join(parameters)
    else:
        item_name = ' '.join(interaction.data['options'][0]['value'].split())
        if len(interaction.data['options']) > 1:
            amount = interaction.data['options'][1]['value']
        else:
            amount = 1

    item_id, item_type = get_it_from_name(item_name)

    if not item_type or item_type != 'item':
        await send_response(content=
                            f"<@{author.id}> What are you trying to use? Check your inventory again to see it's name. Correct usage `val use [item name] [amount]`.")
        return
    if amount <= 0:
        await send_response(content=f"<@{author.id}> The amount must be 1 or higher!")
        return

    if 'heal_power' in ITEMS[item_id]:
        inventory = get_full_inventory_dict(author.id)
        if item_id not in inventory or not inventory[item_id]:
            await send_response(content=
                                f"<@{author.id}> You don't have any **{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** in your inventory!")
            return
        if inventory[item_id] < amount:
            await send_response(content=
                                f"<@{author.id}> You don't have that many **{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** in your inventory!")
            return

        hp_healed = ITEMS[item_id]['heal_power'] * amount
        hp, max_hp = get_current_hp(author.id)

        if hp_healed + hp > max_hp:
            hp_healed = max_hp - hp

        hp += hp_healed

        if hp > max_hp:
            hp = max_hp

        await send_response(content=
                            f"""**{author.name}** consumed **{amount} {ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** \
and replenished **{hp_healed} HP**. Now you have **{hp}/{max_hp} HP**!""")

        set_hp(author.id, hp)
        remove_item(author.id, item_id, amount)

    elif 'effect' in ITEMS[item_id]:
        if item_id == 14:
            STR, AGI, END, INT, LUK, PER = get_traits(author.id)
            update_remove_traits(author.id, [-STR, -AGI, -END, -INT, -LUK, -PER], INT, PER)
            add_trait_points(author.id, sum([STR, AGI, END, INT, LUK, PER]))
            await send_response(content=
                                f"""**{author.name}** used the {ITEMS[item_id]['emoji']} **{ITEMS[item_id]['name']}**. \
Your traits have been reset. Use `/traits` to assign the points back!""")


    else:
        await send_response(content=
                            f"<@{author.id}> **{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** doesn't have any effects, you can't use it")
        return


async def val_add_fuel(channel: discord.TextChannel,
                       author: discord.User,
                       command: str,
                       interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        amount = 1
        parameters = command.split()[2:]
        if not parameters:
            if not parameters:
                await send_response(content=
                                    f"<@{author.id}> What are you trying to use as fuel? Check your inventory again to see it's name. Correct usage `val add/remove [fuel name] [amount]`.")
                return

        if parameters[-1].isnumeric():
            amount = int(parameters[-1])
            parameters.pop()

        item_name = ' '.join(parameters)
    else:
        item_name = ' '.join(interaction.data['options'][0]['value'].split())
        if len(interaction.data['options']) > 1:
            amount = interaction.data['options'][1]['value']
        else:
            amount = 1

    item_id, item_type = get_it_from_name(item_name)

    if not item_type or item_type != 'item':
        await send_response(content=
                            f"<@{author.id}> What are you trying to use as fuel? Check your inventory again to see it's name. Correct usage `val add/remove [fuel name] [amount]`.")
        return
    if 'fuel_power' not in ITEMS[item_id]:
        await send_response(content=
                            "That item is not flammable! Use something like logs, branches, etc. You can use `val help [item]` to view more details about an item.")
        return

    furnaces = get_furnaces_info(author.id)

    if not furnaces:
        await send_response(content=
                            f"<@{author.id}>, you don't have any furnace in your house! Build one using `val build`!")
        return

    eligibe_furnaces = []
    for slot in furnaces:
        if furnaces[slot]['fuel_inside'] == item_id or not furnaces[slot]['fuel_inside']:
            eligibe_furnaces.append(slot)

    if len(furnaces) == 1 and not eligibe_furnaces:
        await send_response(content=
                            f"<@{author.id}>, you need to **remove the current fuel** from your furnace before adding another type!")
        return

    elif len(furnaces) >= 2 and not eligibe_furnaces:
        await send_response(content=
                            f"<@{author.id}> you can't add **{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** to any of your current furnaces, **remove the current fuel** from your furnace before adding another type!")
        return

    if len(eligibe_furnaces) >= 2:
        furnace_to_addf_slot, interaction = await ask_what_furnace(channel, author, item_id, amount,
                                                                   len(eligibe_furnaces),
                                                                   add_fuelm=True, interaction=interaction)
        if not interaction:
            return
        await interaction.response.defer()

    else:
        furnace_to_addf_slot = eligibe_furnaces[0]

    item_done_amount, item_done_id = format_furnace_view('', furnaces, furnace_to_addf_slot,
                                                         author.id,
                                                         just_give_rewards=True)
    if not furnaces[furnace_to_addf_slot]['fuel_inside']:
        add_fuel(author.id, item_id, amount, furnace_to_addf_slot,
                 burn_time=ITEMS[item_id]['fuel_power'])
    else:
        add_fuel(author.id, item_id, amount, furnace_to_addf_slot)

    text = ''
    if item_done_amount:
        text += f"**{author.name}** collected **+{item_done_amount} {ITEMS[item_done_id]['emoji']} {ITEMS[item_done_id]['name']}** from the furnace.\n"

    text += f"**{author.name}** added **{amount} {ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}** as fuel in furnace on slot {furnace_to_addf_slot + 1}.\n" \
            f"Check the burn time left in `val house`."

    if len(furnaces) != len(eligibe_furnaces):
        text += "If you want to add this fuel to another furnace, remove it's current fuel first!"

    await send_response(content=text)


async def val_remove_fuel(channel: discord.TextChannel,
                          author: discord.User,
                          command: str,
                          interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    amount = 0
    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=
                                f"<@{author.id}>, please specify how much fuel to remove! Correct usage: `val remove fuel [amount]`.")
            return

        if parameters[-1].isnumeric():
            amount = int(parameters[-1])
            parameters.pop()

        if not amount:
            await send_response(content=
                                f"<@{author.id}>, please specify how much fuel to remove! Correct usage: `val remove fuel [amount]`.")
            return
    else:
        amount = interaction.data['options'][0]['value']

    furnaces = get_furnaces_info(author.id)

    if not furnaces:
        await send_response(content=
                            f"<@{author.id}>, you don't have any furnace in your house! Build one using `val build`!")
        return

    eligibe_furnaces = []
    for slot in furnaces:
        if furnaces[slot]['fuel_inside']:
            eligibe_furnaces.append(slot)

    if not eligibe_furnaces:
        await send_response(content=f"<@{author.id}>, none of your furnaces have fuel inside!")
        return

    if len(eligibe_furnaces) >= 2:
        furnace_to_remf_slot, interaction = await ask_what_furnace(channel, author, 0, 0, len(eligibe_furnaces),
                                                                   remove_fuelm=True, interaction=interaction)
        if not interaction:
            return
        await interaction.response.defer()

    else:
        furnace_to_remf_slot = eligibe_furnaces[0]

    item_done_amount, item_done_id = format_furnace_view('', furnaces, furnace_to_remf_slot,
                                                         author.id,
                                                         just_give_rewards=True)

    item_id, amount_removed = remove_fuel_with_amount(author.id, furnace_to_remf_slot, amount)
    # function also gives back fuel removed

    text = ''
    if item_done_amount:
        text += f"**{author.name}** collected **+{item_done_amount} {ITEMS[item_done_id]['emoji']} {ITEMS[item_done_id]['name']}** from the furnace.\n"

    text += f"""**{author.name}** removed **{amount_removed} {ITEMS[item_id]['emoji']} """ \
            f"""{ITEMS[item_id]['name']}** {"(you don't get back fuel that already burned partially) " if amount_removed != amount else ''}from the furnace on slot {furnace_to_remf_slot + 1}.\n"""

    await send_response(content=text)


async def val_equipment(channel: discord.TextChannel,
                        author: discord.User,
                        command: str,
                        slash_command: discord.Interaction = None,
                        from_command=False,
                        start_time_cmd=0):
    area = await get_player_area(channel, author)
    if not area:
        return

    if slash_command and slash_command.command:
        send_response = slash_command.edit_original_response
    else:
        send_response = channel.send

    if not slash_command:
        parameters = command.split()[2:]
    else:
        parameters = []
        if 'options' in slash_command.data and slash_command.data['options']:
            parameters.append(str(slash_command.data['options'][0]['value']))

    category_dict = {'pickaxe': 'pickaxe', 'p': 'pickaxe', 'pick': 'pickaxe', 'pickaxes': 'pickaxe',
                     'weapons': 'weapon', 'w': 'weapon', 'weapon': 'weapon',
                     'armor': 'armor', 'a': 'armor', 'armors': 'armor'}

    wanted_category = "pickaxe"
    wanted_area = 0

    if parameters:
        if parameters[0].isnumeric():
            wanted_area = int(parameters[0])
            if wanted_area > area:
                await send_response(content=f"<@{author.id}> You haven't unlocked that zone yet!")
                return

        elif parameters[0] in category_dict:
            wanted_category = category_dict[parameters[0]]

        else:
            await send_response(content=f"<@{author.id}> What are you trying to do?\n"
                                        f"Correct usage: `val equipment [equipment_type] [zone#]`.\n"
                                        f"To equip an item use `val equip [item name]` instead!")
            return

        if len(parameters) == 2 and parameters[1].isnumeric() and not wanted_area:
            wanted_area = int(parameters[1])
            if wanted_area > area:
                await send_response(content=f"<@{author.id}> You haven't unlocked that zone yet!")
                return

        elif len(parameters) == 2 and parameters[1] in category_dict and wanted_category != 'pickaxe':
            wanted_category = category_dict[parameters[1]]

        elif len(parameters) == 2:
            await send_response(content=f"<@{author.id}> What are you trying to do?\n"
                                        f"Correct usage: `val eq [equipment_type] [zone#]`.\n"
                                        f"To equip an item use `val equip [item name]` instead!")
            return

    if not wanted_area:
        wanted_area = area

    # ERROR CHECK DONE ===========================
    eq_message = None
    interaction = None
    view = None
    pickaxe, weapon, helmet, chest = get_all_player_gear(author.id)
    STR, AGI, END, INT, LUK, PER = get_traits(author.id)

    current_category_size = 0
    current_index = 0
    all_equipment = []

    category_selector = {'weapon': WEAPONS, 'armor': ARMORS, 'pickaxe': PICKAXES, 'helmet': HELMETS}
    gear_selector = {'pickaxe': pickaxe, 'weapon': weapon, 'helmet': helmet, 'armor': chest}

    function_selector = {'weapon': get_all_owned_weapons, 'armor': get_all_owned_armors,
                         'pickaxe': get_all_owned_pickaxes, 'helmet': get_all_owned_helmets}

    equip_func_selector = {'weapon': equip_weapon, 'armor': equip_armor, 'pickaxe': equip_pickaxe,
                           'helmet': equip_helmet}

    info_text_selector = {'weapon': general_weapon_info_text, 'armor': general_armor_info_text,
                          'pickaxe': general_pickaxe_info_text, 'helmet': general_helmet_info_text}

    browse_screen = True
    while True:
        if eq_message:
            def check_i(inter):
                return inter.message and inter.message.id == eq_message.id

            try:
                interaction = await bot.wait_for('interaction', timeout=90, check=check_i)
            except asyncio.TimeoutError:
                if from_command:
                    return -1, 0, 0, 0

                for child in view.children:
                    child.disabled = True
                await eq_message.edit(view=view)
                return

            if interaction.user.id != author.id:
                await interaction.response.send_message(
                    content="This is not your command! Use `val equipment` to do this yourself!", ephemeral=True)
                continue

            await interaction.response.defer()
            if from_command and time.time() - start_time_cmd > 90:
                return -1, 0, 0, 0

            if interaction.data['custom_id'] == 'eq_pickaxe':
                wanted_category = 'pickaxe'
                current_index = 0

            elif interaction.data['custom_id'] == 'eq_weapon':
                wanted_category = 'weapon'
                current_index = 0

            elif interaction.data['custom_id'] == 'eq_armor':
                wanted_category = 'armor'
                current_index = 0

            elif interaction.data['custom_id'] == 'eq_helmet':
                wanted_category = 'helmet'
                current_index = 0

            elif interaction.data['custom_id'] == 'eq_arrow_up':
                current_index -= 1
                if current_index < 0:
                    current_index = current_category_size - 1

            elif interaction.data['custom_id'] == 'eq_arrow_down':
                current_index += 1
                if current_index >= current_category_size:
                    current_index = 0

            elif interaction.data['custom_id'] == 'eq_equip':
                equip_func_selector[wanted_category](author.id, all_equipment[current_index][0])
                gear_selector[wanted_category] = all_equipment[current_index][0]

            elif interaction.data['custom_id'] == 'eq_back':
                browse_screen = True

            elif interaction.data['custom_id'] == 'eq_back2':
                return gear_selector.values()

            elif interaction.data['custom_id'] == 'eq_info':
                info_screen = True
                browse_screen = False

        if browse_screen:
            embed = discord.Embed(colour=ZONES[area]['color'])
            embed.set_author(name=f"{author.name}'s equipment", icon_url=author.avatar)
            embed.set_footer(text="Use [val help eq] for more info")

            embed.description = f"**Zone {int_to_roman(area)} {wanted_category}s:**\n\n"

            # Formatting ====================
            all_equipment = function_selector[wanted_category](author.id) + [(0,)]
            current_category_size = len(all_equipment)

            for i, item_id in enumerate(all_equipment):
                if i == current_index:
                    embed.description += f"""__{category_selector[wanted_category][item_id[0]]['emoji']} \
**{category_selector[wanted_category][item_id[0]]['name']}** \
{'**[EQUIPPED]**' if item_id[0] == gear_selector[wanted_category] else ''}__  ⬅\n"""

                else:
                    embed.description += f"""{category_selector[wanted_category][item_id[0]]['emoji']} \
**{category_selector[wanted_category][item_id[0]]['name']}** \
{'**[EQUIPPED]**' if item_id[0] == gear_selector[wanted_category] else ''}\n"""

            if not all_equipment:
                embed.description += f"You don't own any {wanted_category} yet"

            embed.description += 'ㅤ'
            # embed.description += f"\nEquip another {wanted_category} using `val equip [item name]`"

            view = discord.ui.View()
            view.add_item(discord.ui.Button(label='Pickaxe',
                                            emoji=PICKAXES[pickaxe]['emoji'] if PICKAXES[pickaxe]['emoji'] else None,
                                            custom_id='eq_pickaxe',
                                            disabled=wanted_category == 'pickaxe', row=0,
                                            style=discord.ButtonStyle.green if wanted_category == 'pickaxe' else discord.ButtonStyle.grey))

            view.add_item(
                discord.ui.Button(label='Weapon', emoji=WEAPONS[weapon]['emoji'] if WEAPONS[weapon]['emoji'] else None,
                                  custom_id='eq_weapon',
                                  disabled=wanted_category == 'weapon', row=0,
                                  style=discord.ButtonStyle.green if wanted_category == 'weapon' else discord.ButtonStyle.grey))

            view.add_item(discord.ui.Button(emoji='⬆', row=0, custom_id='eq_arrow_up'))

            view.add_item(
                discord.ui.Button(label='Armor ', emoji=ARMORS[chest]['emoji'] if ARMORS[chest]['emoji'] else None,
                                  custom_id='eq_armor',
                                  disabled=wanted_category == 'armor', row=1,
                                  style=discord.ButtonStyle.green if wanted_category == 'armor' else discord.ButtonStyle.grey))

            view.add_item(
                discord.ui.Button(label='Helmet', emoji=HELMETS[helmet]['emoji'] if HELMETS[helmet]['emoji'] else None,
                                  custom_id='eq_helmet',
                                  disabled=wanted_category == 'helmet', row=1,
                                  style=discord.ButtonStyle.green if wanted_category == 'helmet' else discord.ButtonStyle.grey))

            view.add_item(discord.ui.Button(emoji='⬇', row=1, custom_id='eq_arrow_down'))

            if all_equipment and STR < WEAPONS[all_equipment[current_index][0]]['str']:
                view.add_item(
                    discord.ui.Button(label=f"REQ {WEAPONS[all_equipment[current_index][0]]['str']} STR", emoji='⚠',
                                      style=discord.ButtonStyle.blurple, row=2,
                                      disabled=True,
                                      custom_id='eq_equip'))
            else:
                view.add_item(discord.ui.Button(label='EQUIP', emoji='➕', style=discord.ButtonStyle.blurple, row=2,
                                                disabled=not all_equipment or current_index == all_equipment.index(
                                                    (gear_selector[wanted_category],)),
                                                custom_id='eq_equip'))

            view.add_item(discord.ui.Button(label='INFO', emoji='ℹ', style=discord.ButtonStyle.blurple, row=2,
                                            custom_id='eq_info', disabled=not all_equipment))
            if from_command:
                view.add_item(discord.ui.Button(label='BACK', emoji='⬅', style=discord.ButtonStyle.red, row=2,
                                                custom_id='eq_back2'))

        else:
            embed = discord.Embed(colour=ZONES[area]['color'])
            embed.set_author(name=f"{author.name}'s equipment", icon_url=author.avatar)
            embed.description = info_text_selector[wanted_category](
                all_equipment[current_index][0],
                current_index == all_equipment.index((gear_selector[wanted_category],)))

            embed.set_footer(text="You can view this with `val help [item name]` too!")
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label='EQUIP', emoji='➕', style=discord.ButtonStyle.blurple, row=1,
                                            disabled=current_index == all_equipment.index(
                                                (gear_selector[wanted_category],)),
                                            custom_id='eq_equip'))

            view.add_item(discord.ui.Button(label='BACK', emoji='⬅', style=discord.ButtonStyle.red, row=1,
                                            custom_id='eq_back'))

        if not eq_message:
            if from_command:
                eq_message = await slash_command.edit_original_response(embed=embed, view=view)
            else:
                eq_message = await send_response(embed=embed, view=view)
        else:
            await interaction.message.edit(embed=embed, view=view)


async def val_equip(channel: discord.TextChannel,
                    author: discord.User,
                    command: str,
                    interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=
                                f"<@{author.id}> What are you trying to equip? Correct usage: `val equip [item name]`.")
            return

        item_name = ' '.join(parameters)
    else:
        item_name = ' '.join(interaction.data['options'][0]['value'].split())

    item_id, item_type = get_it_from_name(item_name)
    STR, AGI, END, INT, LUK, PER = get_traits(author.id)

    if item_type == 'pickaxe':
        if is_pickaxe_owned(author.id, item_id):
            equip_pickaxe(author.id, item_id)
            await send_response(content=
                                f"**{author.name}** successfully equipped **{PICKAXES[item_id]['emoji']} {PICKAXES[item_id]['name']}**!")
        else:
            await send_response(content=
                                f"<@{author.id}> You don't own this pickaxe! Check your owned pickaxes using `val eq`.")
            return

    elif item_type == 'helmet':
        if is_helmet_owned(author.id, item_id):
            if STR < HELMETS[item_id]['str']:
                await send_response(content=
                                    f"<@{author.id}>, this helmet requires {HELMETS[item_id]['str']} STR!")
                return

            equip_helmet(author.id, item_id)
            await send_response(content=
                                f"**{author.name}** successfully equipped **{HELMETS[item_id]['emoji']} {HELMETS[item_id]['name']}**!")
        else:
            await send_response(content=
                                f"<@{author.id}> You don't own this helmet! Check your owned helmets using `val eq`.")
            return

    elif item_type == 'armor':
        if is_armor_owned(author.id, item_id):
            if STR < ARMORS[item_id]['str']:
                await send_response(content=f"<@{author.id}>, this armor requires {ARMORS[item_id]['str']} STR!")
                return
            equip_armor(author.id, item_id)
            await send_response(content=
                                f"**{author.name}** successfully equipped **{ARMORS[item_id]['emoji']} {ARMORS[item_id]['name']}**!")
        else:
            await send_response(content=
                                f"<@{author.id}> You don't own this armor! Check your owned armors using `val eq`.")
            return

    elif item_type == 'weapon':
        if is_weapon_owned(author.id, item_id):
            if STR < WEAPONS[item_id]['str']:
                await send_response(content=
                                    f"<@{author.id}>, this weapon requires {WEAPONS[item_id]['str']} STR!")
                return
            equip_weapon(author.id, item_id)
            await send_response(content=
                                f"**{author.name}** successfully equipped **{WEAPONS[item_id]['emoji']} {WEAPONS[item_id]['name']}**!")
        else:
            await send_response(content=
                                f"<@{author.id}> You don't own this weapon! Check your owned weapon using `val eq`.")
            return

    else:
        await send_response(content=
                            f"<@{author.id}> What are you trying to equip? Use `val eq` to view the item's name again! Correct usage: `val equip [item name]`.")
        return


async def val_battle(channel: discord.TextChannel,
                     author: discord.User,
                     mentions: typing.List[discord.User],
                     interaction: discord.Interaction = None,
                     zone_boss: int = 0):
    # [area, health, max_health, level, mana, max_mana]
    stats = await get_all_player_stats_battle(channel, author.id)
    if not stats:
        return

    area = stats[0]

    # See if they completed the zone requirements
    if zone_boss:
        zone_boss = area
        if not get_zone_status(author.id, area):  # If they didn't complete the zone req
            await val_explore(channel, author, interaction=interaction)
            return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    players = set(mentions + [author])
    players.discard(bot.user)

    # Check cooldown =======================================================
    for player in players:
        if zone_boss:
            cooldown = get_cooldown(player.id, 20)
            if time.time() - cooldown <= 28800.0:  # 8h
                await cooldown_warning(channel, player, 'progress to another zone', 28800 - int(time.time() - cooldown),
                                       area,
                                       interaction=interaction)
                return
        else:
            cooldown = get_cooldown(player.id, 3)
            if time.time() - cooldown <= 3600.0:
                await cooldown_warning(channel, player, 'battle enemies', 3600 - int(time.time() - cooldown), area,
                                       interaction=interaction)
                return

    if zone_boss and len(players) == 1:
        await send_response(content=f"<@{author.id}>, you are too weak to do this fight alone! Use `/battle party_member1: @user...` and try with some friends!")
        return

    if len(players) > 3:
        await send_response(content=f"<@{author.id}>, the maximum party size is three!")
        return

    if stats[3] < 5:
        await send_response(
            content=f"<@{author.id}>, you are not prepared for a battle yet! This command is unlocked at **level 5**!")
        return

    # If more than 1 player, everyone needs to agree ===========================================
    confirmation_message = None
    if len(players) > 1:
        confirmation_embed = discord.Embed(color=ZONES[area]['color'])
        confirmation_embed.set_author(name=f"{author.name}'s battle!", icon_url=author.avatar)
        if zone_boss:
            confirmation_embed.description = f"""Press on **"I agree"** if you would like to join a battle against {ZONE_REQUIREMENTS[area]['battle_against']}, with **{author.name}**!\n\n"""
        else:
            confirmation_embed.description = f"""Press on **"I agree"** if you would like to join a battle with **{author.name}**!\n\n"""

        for player in players:
            user_area = await get_player_area(channel, player, ping=author.id)
            if not user_area:
                return

            # TODO: if zone_boss and max area > area of author

            if user_area != area:
                await send_response(content=f"<@{author.id}>, you can't add {player.name} to your party because"
                                            f" they are in another zone!")
                return

            try:
                cmd = DATA_CACHE[player.id]['cmd']
            except KeyError:
                cmd = 0
                DATA_CACHE[player.id] = {'cmd': 0}

            if cmd and player != author:
                await send_response(content=f"<@{author.id}>, you can't add {player.name} to your party because"
                                            f" they are in another command!(`{COMMANDS[cmd]['name']}`)")
                return

            if zone_boss:
                zone_status = get_zone_status(player.id, area)
                if not zone_status:
                    await send_response(content=f"{author.mention}, you can't add **{player.name}** to the party, "
                                                f"{ZONE_REQUIREMENTS[area]['req_not_done_warning']} Use `/explore` to learn more.")
                    return

            confirmation_embed.description += f"**{player.name} - Pending** ⏳\n"

        confirmation_embed.set_thumbnail(url=random.choice(ZONES[area]['image_link']))
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(label='I agree', emoji='✔', style=discord.ButtonStyle.green, custom_id='agree_bt'))
        view.add_item(
            discord.ui.Button(label='I refuse', emoji='✖', style=discord.ButtonStyle.red, custom_id='refuse_bt'))
        confirmation_message = await send_response(content=
                                                   ', '.join([f"<@{player.id}>" for player in
                                                              players]) + ' do you want to battle?',
                                                   embed=confirmation_embed, view=view)

        players_who_agreed = []
        INTERACTION_BUCKET[confirmation_message.id] = []

        while True:
            if len(players) == len(players_who_agreed):
                await asyncio.sleep(1)
                break

            await asyncio.sleep(0.1)
            if not INTERACTION_BUCKET[confirmation_message.id]:
                continue

            interaction = INTERACTION_BUCKET[confirmation_message.id].pop(0)

            if interaction.user not in players:
                await interaction.response.send_message(
                    content=f"You weren't invited into the party by **{author.name}**!", ephemeral=True)
                continue

            elif interaction.data['custom_id'] == 'refuse_bt':
                for child in view.children:
                    child.disabled = True
                await interaction.response.edit_message(view=view)
                if interaction.user.id == author.id:
                    await channel.send(f"<@{author.id}> has cancelled the battle!")
                else:
                    await confirmation_message.reply(
                        f"<@{author.id}>, the battle was canceled, because <@{interaction.user.id}> refused to join your party!")
                del INTERACTION_BUCKET[confirmation_message.id]
                return

            elif interaction.data['custom_id'] == 'agree_bt':
                players_who_agreed.append(interaction.user)
                if zone_boss:
                    confirmation_embed.description = f"""Press on **"I agree"** if you would like to join a battle against {ZONE_REQUIREMENTS[area]['battle_against']}, with **{author.name}**!

"""
                else:
                    confirmation_embed.description = f"""Press on **"I agree"** if you would like to join a battle with **{author.name}**!

"""
                for player in players:
                    if player in players_who_agreed:
                        confirmation_embed.description += f"**{player.name} - Agreed** ✅\n"
                    else:
                        confirmation_embed.description += f"**{player.name} - Pending** ⏳\n"

                if not INTERACTION_BUCKET[confirmation_message.id]:
                    await interaction.response.edit_message(embed=confirmation_embed)
                else:
                    await interaction.response.defer()

    # GATHER BATTLE INFO =========================================
    player_info = {}

    free_y = [0, 1, 2, 3]

    player_emojis = ["<:player_1_placeholder:1026449581325701120>", "<:player_2_placeholder:1026449604151103569>",
                     "<:player_3_placeholder:1026449617908404276>"]

    for player in players:
        area, hp, max_hp, level, xp, mana, max_mana = await get_all_player_stats_battle(channel, player.id,
                                                                                        ping=author.id)

        if level < 5:
            await channel.send(content=f"<@{author.id}>, you can't add <@{player}> to your party because they "
                                       f"are not prepared! They unlock this command at **level 5**!")
            return

        STR, AGI, END, INT, LUK, PER = get_traits(player.id)
        pickaxe, weapon, helmet, chest = get_all_player_gear(player.id)

        attack = 2 * STR * ('normal' == WEAPONS[weapon]['type']) + int(
            1.5 * AGI * ('light' == WEAPONS[weapon]['type'])) + WEAPONS[weapon]['at']

        defense = HELMETS[helmet]['def'] + ARMORS[chest]['def'] + AGI // 3 + STR // 2 + END

        speed_divider = 50
        if HELMETS[helmet]['type'] == 'heavy':
            speed_divider += 15
        elif HELMETS[helmet]['type'] == 'normal':
            speed_divider += 5

        if ARMORS[chest]['type'] == 'heavy':
            speed_divider += 35
        elif ARMORS[chest]['type'] == 'normal':
            speed_divider += 25

        player_info[player.id] = {'user': player, 'zone': area, 'hp': hp, 'max_hp': max_hp, 'mana': mana,
                                  'max_mana': max_mana, 'xp': xp,
                                  'level': level, 'str': STR, 'agi': AGI, 'end': END, 'int': INT,
                                  'luk': LUK, 'per': PER, 'at': attack, 'def': defense, 'weapon': weapon,
                                  'helmet': helmet, 'chest': chest, 'turn_speed': round(AGI / speed_divider, 2) + 1,
                                  'turn_left': 0, 'mana_regen': round(INT / 50, 2), 'effects': {},
                                  'bonus': {'def': 0, 'at': 0, 'turn': 0},
                                  'last_used': [0, 0], 'emoji': player_emojis.pop(0)}

        if zone_boss:
            player_info[player.id]['x'] = 0
            player_info[player.id]['y'] = random.choice(free_y)
            free_y.remove(player_info[player.id]['y'])

    group_level = math.ceil(sum([player_info[user]['level'] for user in player_info]) / len(player_info))

    highest_level = max([player_info[user]['level'] for user in player_info])
    if group_level + 0.2 * highest_level < highest_level:
        group_level = int(group_level + 0.2 * highest_level)

    boss_info = get_enemy_for_battle(player_info[author.id]['zone'], group_level, len(player_info),
                                     boss=bool(zone_boss))

    # ASK IF READY ================================================================================================
    embed = discord.Embed(color=ZONES[player_info[author.id]['zone']]['color'])
    embed.set_author(name=f"{author.name}'s battle!", icon_url=author.avatar)
    embed.set_footer(text='The battle will begin when all players are ready!')

    embed.set_thumbnail(url=random.choice(ZONES[player_info[author.id]['zone']]['image_link']))
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Ready', emoji='✔', custom_id='fight_bt', disabled=True,
                                    style=discord.ButtonStyle.blurple))
    view.add_item(discord.ui.Button(label='Flee battle', emoji='💨', custom_id='flee_bt', disabled=True,
                                    style=discord.ButtonStyle.red))

    embed.description = f"""Are you prepared for this fight?
    
You have {random.choice(HUNT_PHASES_found)} a **Lv. {boss_info['level']} {BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}**!
{EMOJIS['hp']} Health: {boss_info['hp']}
{EMOJIS['at']} Damage: ~{boss_info['at']}
—————————————————
"""

    for player in player_info:
        DATA_CACHE[player]['cmd'] = 3

    fight_message_sent = 0
    interaction = None
    ready_to_fight = set()
    fight_message = confirmation_message
    check = None

    if fight_message:
        INTERACTION_BUCKET[fight_message.id] = []

    while True:
        if fight_message_sent:
            await asyncio.sleep(0.1)

            if not INTERACTION_BUCKET[fight_message.id]:
                continue

            interaction = INTERACTION_BUCKET[fight_message.id].pop(0)

            if interaction.user.id not in player_info:
                await interaction.response.send_message(content=f"You are not part of this `battle`!", ephemeral=True)
                continue

            elif interaction.data['custom_id'] == 'fight_bt':
                ready_to_fight.add(interaction.user.id)

            elif interaction.data['custom_id'] == 'flee_bt':
                DATA_CACHE[interaction.user.id]['cmd'] = 0
                del player_info[interaction.user.id]
                ready_to_fight.clear()

                if zone_boss:
                    update_cooldown_set(interaction.user.id, 20, time.time() - 3300)
                else:
                    update_cooldown_set(interaction.user.id, 3, time.time() - 3300)

                if player_info:
                    author = player_info[random.choice(list(player_info))]['user']
                await channel.send(F"<@{interaction.user.id}> has fled the battle!")

        embed.clear_fields()
        for player in player_info:
            embed.add_field(
                name=f"{player_info[player]['user'].name} - Lv. {player_info[player]['level']} {'✅ Ready' if player in ready_to_fight else ''}",
                value=f"""**{EMOJIS['hp']} {player_info[player]['hp']}/{player_info[player]['max_hp']} \
{EMOJIS['at']} {player_info[player]['at']} \
{EMOJIS['def']} {player_info[player]['def']}
{WEAPONS[player_info[player]['weapon']]['emoji']} {WEAPONS[player_info[player]['weapon']]['name']}
{HELMETS[player_info[player]['helmet']]['emoji']} {HELMETS[player_info[player]['helmet']]['name']}
{ARMORS[player_info[player]['chest']]['emoji']} {ARMORS[player_info[player]['chest']]['name']}**
""", inline=False)

        if not player_info:
            embed.description = f"""The enemy escaped...
            
**Lv. {boss_info['level']} {BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}**!
{EMOJIS['hp']} Health: {boss_info['hp']}
{EMOJIS['at']} Damage: ~{boss_info['at']}
—————————————————

{'** Everyone **' if len(mentions) else f"**{author.name}**"} fled the battle!"""
            embed.set_footer(
                text=f"{'You' if not len(mentions) else 'Everyone'} received a cooldown penalty for fleeing!")

        if not fight_message_sent:
            if fight_message:
                await fight_message.edit(embed=embed, view=view, content='')
            else:
                fight_message = await send_response(embed=embed, view=view)

            for child in view.children:
                child.disabled = False

            def check(inter):
                return inter.message and inter.message.id == fight_message.id

            await fight_message.edit(view=view)

            INTERACTION_BUCKET[fight_message.id] = []

            fight_message_sent = 1
        else:
            if ready_to_fight and len(ready_to_fight) == len(player_info):
                await interaction.response.defer()
                del INTERACTION_BUCKET[fight_message.id]
                break

            if not player_info:
                for child in view.children:
                    child.disabled = True

            if not INTERACTION_BUCKET[fight_message.id]:
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.defer()

            if not player_info:
                del INTERACTION_BUCKET[fight_message.id]
                return

    # FIGHT LOGIC =======================================================

    battle_embed = discord.Embed(color=ZONES[player_info[author.id]['zone']]['color'])
    # No thumbnail because makes mobile version look horrible
    battle_embed.set_author(name=f"{author.name}'s battle!", icon_url=author.avatar)

    player_cycle = itertools.cycle(player_info)
    players_turn = player_cycle.__next__()
    player_info[players_turn]['turn_left'] += player_info[players_turn]['turn_speed']
    player_info[players_turn]['time'] = time.time()

    logs = collections.deque(["**1|**The enemy is waiting for your move", '', '', '', ''], maxlen=5)
    old_interaction = interaction
    interaction: discord.Interaction = None

    if zone_boss:
        boss_logics.BOSSES[area]['board_init'](player_info, boss_info)

    view = get_buttons(player_info, players_turn, boss_info)
    boss_info['turn'] = 1
    boss_info['debuffs']: typing.Dict = {}

    battle_start_time = time.time()
    everyone_died = False

    # GAME LOOP ===========================================================================================
    # GAME LOOP ===========================================================================================
    # GAME LOOP ===========================================================================================

    while True:
        if interaction:
            timed_out = False
            try:
                interaction = await bot.wait_for('interaction', timeout=90, check=check)
            except asyncio.TimeoutError:
                timed_out = True
                interaction = old_interaction
                interaction.data['custom_id'] = 'action_bt'

            if not timed_out and interaction.user.id not in player_info:
                await interaction.response.send_message(content="This is not your battle! Use `val battle` "
                                                                "to start one yourself!", ephemeral=True)
                continue

            elif not timed_out and interaction.user.id != players_turn:
                await interaction.response.send_message(content=f"It's <@{players_turn}>'s turn!", ephemeral=True)
                continue

            if time.time() - player_info[players_turn]['time'] > 90:
                timed_out = True
                interaction.data['custom_id'] = 'action_bt'

            turns_used = 1 if not timed_out else -1
            if interaction.data['custom_id'] == 'action_bt':
                if not timed_out:
                    await interaction.response.defer()
                    turns_used, interaction = await action_screen(interaction, player_info, boss_info, logs,
                                                                  battle_embed)

                if turns_used == -2:
                    timed_out = True

                # Flee battle code -1
                if turns_used < 0:
                    DATA_CACHE[players_turn]['cmd'] = 0
                    if timed_out:
                        logs.appendleft(f"**{player_info[players_turn]['user'].name}** died...")
                        await send_response(content=
                                            f"**{player_info[players_turn]['user'].name}** took to long to react so the **{BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}** killed them!")
                    else:
                        logs.appendleft(f"**{player_info[players_turn]['user'].name}** died...")
                        await send_response(
                            content=f"**{player_info[players_turn]['user'].name}** tired to flee the battle, but the **{BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}** noticed and killed them!")

                    player_death_handling(players_turn, zone_boss)
                    new_player = list(reversed([player_cycle.__next__() for i in player_info]))
                    new_player.remove(players_turn)
                    player_cycle = itertools.cycle(new_player)
                    del player_info[players_turn]
                    turns_used = 1

                else:
                    player_info[players_turn]['turn_left'] -= turns_used

            elif interaction.data['custom_id'] == 'uselast_bt':
                # TODO: later add a use time to items and change here
                log_msg = use_item(player_info, players_turn, player_info[players_turn]['last_used'][0], -1)
                turns_used = 1
                player_info[players_turn]['turn_left'] -= turns_used
                logs.appendleft(log_msg)

            elif zone_boss and not interaction.data['custom_id'][0].isnumeric():
                await interaction.response.defer()
                BOSSES[area]['button_actions'](player_info, boss_info, interaction.data['custom_id'], players_turn)

            damage_given, effects_applied = 0, {}
            if turns_used:
                if players_turn in player_info and interaction.data['custom_id'][0].isnumeric():  # like 1_bt, 2_bt
                    if not interaction.response.is_done():
                        await interaction.response.defer()

                    # PROCESS ATTACK OPTIONS ==========================================================================
                    damage_given, effects_applied, log_msg = process_move(player_info, boss_info,
                                                                          interaction.data['custom_id'], players_turn)

                    if zone_boss:
                        log_msg = BOSSES[area]['damage_handler'](player_info, boss_info, players_turn, damage_given,
                                                                 effects_applied)
                    else:
                        # Take the hp and apply effects
                        boss_info['hp'] -= damage_given
                        if boss_info['hp'] < 0:
                            boss_info['hp'] = 0

                        for effect in effects_applied:
                            boss_info['debuffs'][effect] = effects_applied[effect]

                    logs.appendleft(log_msg)

                # If they still have turns left, let them do it, otherwise next player
                if players_turn in player_info and player_info[players_turn]['turn_left'] // 1:
                    logs.appendleft(
                        f"**{player_info[players_turn]['user'].name}** has **{int(player_info[players_turn]['turn_left'] // 1)} turns** left!")

                else:
                    if player_info:
                        if players_turn in player_info and boss_info['hp']:
                            if zone_boss:
                                BOSSES[area]['move_processor'](player_info, boss_info, logs, players_turn)
                            else:
                                process_boss_move(player_info, boss_info, logs, players_turn)

                        for _ in player_info:
                            players_turn = player_cycle.__next__()

                            if player_info[players_turn]['hp'] <= 0:
                                continue

                            break
                        else:
                            everyone_died = True

                        # Increases total turn count
                        boss_info['turn'] += 1

                        # Adds the turns to the player
                        player_info[players_turn]['turn_left'] += player_info[players_turn]['turn_speed']

                        # Set time they started to current time and check if 90s passed
                        player_info[players_turn]['time'] = time.time()

                        # Regenerate their mana
                        player_info[players_turn]['mana'] += player_info[players_turn]['mana_regen']
                        if player_info[players_turn]['mana'] > player_info[players_turn]['max_mana']:
                            player_info[players_turn]['mana'] = player_info[players_turn]['max_mana']

                if player_info:
                    view = get_buttons(player_info, players_turn, boss_info)
                else:
                    view = discord.ui.View()
        # MAIN SCREEN TEXT ===========================================================================================
        log_msg = '\n'.join(logs)

        battle_embed.description = f"""
Wait until it's your turn! You have 90s to react!
**Lv. {boss_info['level']} {BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}**
{EMOJIS['hp']} **{boss_info['hp']}/{boss_info['max_hp']}**
{get_hp_bar(boss_info['hp'], boss_info['max_hp'])}\
{get_effects(boss_info['debuffs'])}\
———————————————
{log_msg}
———————————————
{BOSSES[area]['map_getter'](player_info, boss_info) if zone_boss else ''}\
> **Party:**
{(format_battle_info(player_info, reversed([player_cycle.__next__() for i in player_info]))) if player_info else f"{'**Everyone**' if len(mentions) > 1 else f'**{author.name}**'} fled the battle..."}
"""
        # Goes over the effects of all people and deletes if done
        process_player_effects(player_info)
        # IF PLAYERS WON ===========================================================================================
        if boss_info['hp'] <= 0:
            for child in view.children:
                child.disabled = True
            await interaction.message.edit(embed=battle_embed, view=view, content="")
            await asyncio.sleep(1.5)
            player_names = ', '.join([f"{player_info[i]['user'].name}" for i in player_info])
            rewards_text = f""""""
            for player in player_info:
                if not player_info[player]['hp']:
                    rewards_text += f"\n**{player_info[player]['user'].name}:**\ndied\n"
                    player_death_handling(player, zone_boss)
                else:
                    set_hp(player, player_info[player]['hp'])
                    set_mana(player, player_info[player]['mana'])
                    rewards_text += f"\n**{player_info[player]['user'].name}:**\n"
                    rewards_text += give_battle_rewards(player,
                                                        player_info[player]['level'],
                                                        player_info[player]['xp'],
                                                        player_info[player]['zone'],
                                                        boss_info['id'], zone_boss=zone_boss)

                update_cooldown(player, 3 if not zone_boss else 20)
                DATA_CACHE[player]['cmd'] = 0

            battle_embed.description = f"""
You won!
**Lv. {boss_info['level']} {BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}**
{EMOJIS['hp']} **{boss_info['hp']}/{boss_info['max_hp']}**
{get_hp_bar(boss_info['hp'], boss_info['max_hp'])}
———————————————
**{player_names}** {'has' if len(player_info) == 1 else 'have'} defeated the **{BATTLE_ENEMIES[boss_info['id']]['emoji']} \
{BATTLE_ENEMIES[boss_info['id']]['name']}!** Well done!

**💰 Rewards:**
{rewards_text}
"""
            battle_embed.set_footer(
                text=f"♟ Total turns: {boss_info['turn'] - 1} | ⏱ Time elapsed: {get_pretty_time(int(time.time() - battle_start_time))}")
            view = discord.ui.View()

            await interaction.message.edit(embed=battle_embed, view=view)
            return

        # IF PLAYERS LOST ===========================================================================================
        elif everyone_died:
            for child in view.children:
                child.disabled = True
            await interaction.message.edit(embed=battle_embed, view=view, content="")
            await asyncio.sleep(1.5)
            player_names = ', '.join([f"{player_info[i]['user'].name}" for i in player_info])
            battle_embed.description = f"""
You lost!
**Lv. {boss_info['level']} {BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}**
{EMOJIS['hp']} **{boss_info['hp']}/{boss_info['max_hp']}**
{get_hp_bar(boss_info['hp'], boss_info['max_hp'])}
———————————————
The **{BATTLE_ENEMIES[boss_info['id']]['emoji']} {BATTLE_ENEMIES[boss_info['id']]['name']}** killed \
**{player_names}**!

Better luck next time!
"""
            battle_embed.set_footer(
                text=f"♟ Total turns: {boss_info['turn'] - 1} | ⏱ Time elapsed: {get_pretty_time(int(time.time() - battle_start_time))}")
            view = discord.ui.View()

            for player in player_info:
                player_death_handling(author.id, zone_boss)
                DATA_CACHE[player]['cmd'] = 0

            await interaction.message.edit(embed=battle_embed, view=view)
            return

        if not interaction:
            await fight_message.edit(embed=battle_embed, view=view, content=f"<@{players_turn}>'s turn!")
            interaction = 1
        else:
            if not player_info:
                for child in view.children:
                    child.disabled = True
                await interaction.message.edit(embed=battle_embed, view=view, content=f"Battle canceled!")
                return

            await fight_message.edit(embed=battle_embed, view=view, content=f"<@{players_turn}>'s turn!")


def give_battle_rewards(player_id, level, current_xp, zone, enemy_id, zone_boss):
    reward_text = ""
    rewards = {'crates': [], 'items': [], 'xp': 0}
    if not zone_boss and zone == 1:
        if enemy_id == 5:  # Basilisk
            if random_float(0, 99) <= 2:
                rewards['crates'].append((4, 1))
            elif random_float(0, 99) <= 8:
                rewards['crates'].append((3, 1))
            elif random_float(0, 99) <= 50:
                rewards['crates'].append((2, 1))
            else:
                rewards['crates'].append((1, 1))

            rewards['xp'] = random.randint(1300 + level ** 2, 1400 + level ** 2)
        else:
            if enemy_id == 3:
                rewards['xp'] = random.randint(1700 + level ** 2, 1950 + level ** 2)
                if random_float(0, 99) <= 15:
                    rewards['items'].append((8, 1))
            else:
                rewards['xp'] = random.randint(1500 + level ** 2, 1700 + level ** 2)

            if random_float(0, 99) <= 1:
                rewards['crates'].append((4, 1))
            elif random_float(0, 99) <= 5:
                rewards['crates'].append((3, 1))
            elif random_float(0, 99) <= 30:
                rewards['crates'].append((2, 1))
            else:
                rewards['crates'].append((1, 1))

    elif not zone_boss and zone == 2:
        if enemy_id == 8:
            if random_float(0, 99) <= 2:
                rewards['crates'].append((4, 1))
            elif random_float(0, 99) <= 8:
                rewards['crates'].append((3, 1))
            elif random_float(0, 99) <= 50:
                rewards['crates'].append((2, 1))

            else:
                rewards['crates'].append((1, 1))

            rewards['xp'] = random.randint(2900 + level ** 2, 3300 + level ** 2)
        else:
            if enemy_id == 9:
                rewards['xp'] = random.randint(3700 + level ** 2, 4100 + level ** 2)
                if random_float(0, 99) <= 15:
                    rewards['items'].append((8, 1))
            else:
                rewards['xp'] = random.randint(3300 + level ** 2, 3700 + level ** 2)

            if random_float(0, 99) <= 1:
                rewards['crates'].append((4, 1))
            elif random_float(0, 99) <= 5:
                rewards['crates'].append((3, 1))
            elif random_float(0, 99) <= 30:
                rewards['crates'].append((2, 1))
            else:
                rewards['crates'].append((1, 1))

    elif zone_boss == 1:
        if random_float(0, 99) <= 3:
            rewards['crates'].append((4, 1))
        elif random_float(0, 99) <= 8:
            rewards['crates'].append((3, 1))
        elif random_float(0, 99) <= 30:
            rewards['crates'].append((2, 2))
        else:
            rewards['crates'].append((1, 3))

        rewards['items'].append((14, 1))
        rewards['xp'] = random.randint(2000 + level ** 2, 2200 + level ** 2)

        advance_zone(player_id, 2)
        reward_text += f"**Advanced to `zone II`**\n"

    for crate in rewards['crates']:
        add_crates(player_id, crate[0], crate[1])
        reward_text += f"**{crate[1]} {CRATES[crate[0]]['emoji']} {CRATES[crate[0]]['name']}**\n"

    for item in rewards['items']:
        add_item(player_id, item[0], item[1])
        reward_text += f"**{item[1]} {ITEMS[item[0]]['emoji']} {ITEMS[item[0]]['name']}**\n"

    reward_text += f"**{rewards['xp']} XP**\n"
    if rewards['xp'] + current_xp >= NEXT_XP[level]:
        level_up(player_id, level + 1, current_xp + rewards['xp'] - NEXT_XP[level])
        reward_text += f"**Leveled up! +5 {EMOJIS['trait']} Trait Points!**"
    else:
        add_xp(player_id, rewards['xp'])

    return reward_text


def player_death_handling(player_id, boss):
    if boss:
        set_hp(player_id, 1)
        set_mana(player_id, 0)
        update_cooldown(player_id, 20)
    else:
        set_hp(player_id, 1)
        set_mana(player_id, 0)
        update_cooldown(player_id, 3)


def process_player_effects(player_info):
    for player in player_info:
        if player_info[player]['effects']:
            for effect in copy.deepcopy(player_info[player]['effects']):
                player_info[player]['effects'][effect][0] -= 1

                if not player_info[player]['effects'][effect][0]:
                    if effect == '3_bt':
                        player_info[player]['bonus']['def'] -= player_info[player]['effects'][effect][1]
                        del player_info[player]['effects'][effect]


def get_effects(effects):
    text = ''

    if 'on_fire' in effects:
        text += f"\n🔥 On fire ({effects['on_fire'][0]} turns left)"

    return text + '\n'


def use_item(player_info, player, item, total_in_inv):
    if 'heal_power' in ITEMS[item]:
        player_info[player]['hp'] += ITEMS[item]['heal_power']
        if player_info[player]['hp'] > player_info[player]['max_hp']:
            player_info[player]['hp'] = player_info[player]['max_hp']

        if total_in_inv != -1:
            player_info[player]['last_used'] = [item, total_in_inv - 1]
        else:
            player_info[player]['last_used'][1] -= 1

        if not player_info[player]['last_used'][1]:
            player_info[player]['last_used'] = [0, 0]

        remove_item(player, item, 1)
        return f"**{player_info[player]['user'].name}** used a **{ITEMS[item]['emoji']} " \
               f"{ITEMS[item]['name']}** and restored **{ITEMS[item]['heal_power']} HP!**"


def get_buttons(player_info, player_id, boss_info):
    view = discord.ui.View()
    weapon = player_info[player_id]['weapon']

    if 'x' in player_info[player_id]:
        X = player_info[player_id]['x']
        Y = player_info[player_id]['y']
        view.add_item(discord.ui.Button(emoji='⬛', disabled=True, row=0))
        view.add_item(
            discord.ui.Button(emoji='🔼', custom_id='up_bt', disabled=Y == 0 or not not boss_info['board'][Y - 1][X],
                              row=0))
        view.add_item(discord.ui.Button(emoji='⬛', disabled=True, row=0))
        view.add_item(
            discord.ui.Button(emoji='◀', custom_id='left_bt', disabled=X == 0 or not not boss_info['board'][Y][X - 1],
                              row=1))
        view.add_item(discord.ui.Button(emoji='🔽', custom_id='down_bt',
                                        disabled=Y == BOSSES[player_info[player_id]['zone']]['max_y'] or not not
                                        boss_info['board'][Y + 1][X], row=1))
        view.add_item(discord.ui.Button(emoji='▶', custom_id='right_bt',
                                        disabled=X == BOSSES[player_info[player_id]['zone']]['max_x'] or not not
                                        boss_info['board'][Y][X + 1], row=1))

    # TODO: make it so its required to have a weapon to enter the battle
    for move in WEAPONS[weapon]['moves']:
        view.add_item(discord.ui.Button(label=WEAPON_MOVES[move]['name'], custom_id=f'{move}_bt',
                                        emoji=WEAPONS[weapon]['emoji'] if WEAPONS[weapon]['emoji'] else
                                        WEAPON_MOVES[move]['emoji'],
                                        style=discord.ButtonStyle.green,
                                        disabled='mana' in WEAPON_MOVES[move] and player_info[player_id]['mana'] <
                                                 WEAPON_MOVES[move]['mana'],
                                        row=2))

    view.add_item(discord.ui.Button(label='Action', emoji='➕', custom_id='action_bt', style=discord.ButtonStyle.grey,
                                    row=2))

    if player_info[player_id]['last_used'][0]:
        view.add_item(
            discord.ui.Button(
                label=f"Use {ITEMS[player_info[player_id]['last_used'][0]]['name']}: {player_info[player_id]['last_used'][1]}",
                emoji=ITEMS[player_info[player_id]['last_used'][0]]['emoji'],
                custom_id='uselast_bt',
                style=discord.ButtonStyle.grey,
                row=2))

    view.add_item(discord.ui.Button(label=f"""{player_info[player_id]['user'].name}: {player_info[player_id]['turn_left']: .2f} turns left""", style=discord.ButtonStyle.grey,
                                    row=4, disabled=True))

    return view


def process_move(player_info, boss_info, move_id, player_id):
    crit_multiplier = 1
    if random_float(0, 99) <= 4 + player_info[player_id]['luk'] * 0.08 + player_info[player_id]['agi'] * 0.01:
        crit_multiplier = 2

    damage = 0
    effects_applied = {}
    log_msg = ""

    if move_id == '1_bt':
        player_info[player_id]['turn_left'] -= 1
        damage = random.randint(int(player_info[player_id]['at'] - player_info[player_id]['at'] * 0.1),
                                (player_info[player_id]['at'])) * crit_multiplier
        if crit_multiplier > 1:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** __CRITICAL__ hit {BATTLE_ENEMIES[boss_info['id']]['emoji']} for **{damage} HP**"
        else:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hit {BATTLE_ENEMIES[boss_info['id']]['emoji']} for **{damage} HP**"

    elif move_id == '2_bt':
        player_info[player_id]['turn_left'] -= 1
        player_info[player_id]['mana'] -= 5
        effects_applied['on_fire'] = [math.ceil(player_info[player_id]['int'] / 5),
                                      player_info[player_id]['int'] + player_info[player_id]['at']]

    elif move_id == '3_bt':
        player_info[player_id]['turn_left'] -= 1
        added_def = player_info[player_id]['def'] // 2
        for player in player_info:
            if player != player_id:
                player_info[player]['bonus']['def'] += added_def
                player_info[player]['effects']['3_bt'] = [1, added_def]

        log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** defends the party!"

    return damage, effects_applied, log_msg


def process_boss_move(player_info, boss_info, logs, player_id):
    if boss_info['debuffs']:
        if 'on_fire' in boss_info['debuffs']:
            boss_info['debuffs']['on_fire'][0] -= 1
            boss_info['hp'] -= boss_info['debuffs']['on_fire'][1]
            logs.appendleft(
                f"**{boss_info['turn']}|** 🔥 deals **{boss_info['debuffs']['on_fire'][1]} damage** to the {BATTLE_ENEMIES[boss_info['id']]['emoji']}!")

            if not boss_info['debuffs']['on_fire'][0]:
                del boss_info['debuffs']['on_fire']

    if random_float(0, boss_info['at']) <= 0.5 + player_info[player_id]['agi'] * 0.5:
        logs.appendleft(
            f"**{boss_info['turn']}|** **{player_info[player_id]['user'].name}** dodged the {BATTLE_ENEMIES[boss_info['id']]['emoji']}!")
    else:
        damage = random.randint(int(boss_info['at'] - boss_info['at'] * 0.05), boss_info['at']) - \
                 player_info[player_id]['def']

        damage -= player_info[player_id]["bonus"]['def']

        if damage < 3:
            damage = random.randint(1, 3)

        player_info[player_id]['hp'] -= damage
        if player_info[player_id]['hp'] < 0:
            player_info[player_id]['hp'] = 0

        logs.appendleft(
            f"**{boss_info['turn']}|** {BATTLE_ENEMIES[boss_info['id']]['emoji']} hit **{player_info[player_id]['user'].name}** for **{damage} hp**")

    if boss_info['hp'] < 0:
        boss_info['hp'] = 0


def format_battle_info(player_info: typing.Dict, player_order: typing.List[int]):
    text = ""
    for player in player_order:
        text += f"""{player_info[player]['emoji']} **{player_info[player]['user'].name} — Lv.{player_info[player]['level']}**"""

        if player_info[player]['mana']:
            text += f"""\n{EMOJIS['mana']} **{player_info[player]['mana']:.2f}/{player_info[player]['max_mana']}**"""

        text += f"""
{EMOJIS['hp']} **{player_info[player]['hp']}/{player_info[player]['max_hp']}**
{get_hp_bar(player_info[player]['hp'], player_info[player]['max_hp'])}

"""

        if player_info[player]['effects']:
            text += "**Debuffs:** "
            for effect in player_info[player]['effects']:
                if effect == '3_bt':
                    text += f"**🛡 Protected: ({player_info[player]['effects'][effect][0]} turn, {player_info[player]['effects'][effect][1]} DEF)**, "

    return text


def get_enemy_for_battle(zone: int, level: int, party_size: int, boss=False):
    if boss:
        if zone == 1:
            return {'id': 6, 'hp': 200 * party_size, 'max_hp': 200 * party_size, 'level': level, 'at': 100}

    if zone == 1:
        enemy = random.choice((1, 2, 3, 4, 5))
        at = (random.randint(BATTLE_ENEMIES[enemy]['at_min'], BATTLE_ENEMIES[enemy]['at_max'])
              + (level - 1) * BATTLE_ENEMIES[enemy]['at+'])

        hp = (random.randint(BATTLE_ENEMIES[enemy]['hp_min'], BATTLE_ENEMIES[enemy]['hp_max'])
              + (level - 1) * BATTLE_ENEMIES[enemy]['hp+'])

        level = random.randint(level - 1, level + 1)
        if level < 0:
            level = 1

        return {'hp': hp, 'max_hp': hp, 'level': level, 'at': at, 'id': enemy}

    elif zone == 2:
        enemy = random.choice((7, 8, 9, 10))
        at = (random.randint(BATTLE_ENEMIES[enemy]['at_min'], BATTLE_ENEMIES[enemy]['at_max'])
              + (level - 1) * BATTLE_ENEMIES[enemy]['at+'])

        hp = (random.randint(BATTLE_ENEMIES[enemy]['hp_min'], BATTLE_ENEMIES[enemy]['hp_max']) * party_size
              + (level - 1) * BATTLE_ENEMIES[enemy]['hp+'])

        level = random.randint(level - 1, level + 1)
        if level < 0:
            level = 1

        return {'hp': hp, 'max_hp': hp, 'level': level, 'at': at, 'id': enemy}


async def action_screen(interaction, player_info, boss_info, logs, embed):
    edited_button = False
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Use item', emoji=EMOJIS['heal'], custom_id='use_bt',
                                    style=discord.ButtonStyle.blurple))

    view.add_item(discord.ui.Button(label='Swap gear', emoji='⚒', custom_id='swap_bt',
                                    style=discord.ButtonStyle.blurple))

    view.add_item(
        discord.ui.Button(label='Flee battle', emoji='💨', custom_id='flee_bt', style=discord.ButtonStyle.red))
    view.add_item(discord.ui.Button(label='Back', emoji='⬅', custom_id='back_bt',
                                    style=discord.ButtonStyle.red))

    players_turn = interaction.user.id

    def check(inter):
        return inter.message.id == interaction.message.id

    while True:
        if edited_button:
            try:
                interaction = await bot.wait_for('interaction', timeout=90, check=check)
            except asyncio.TimeoutError:
                return -2, interaction

            if interaction.user.id not in player_info:
                await interaction.response.send_message(
                    content="This is not your battle! Use `val battle` to start one yourself!", ephemeral=True)
                continue
            elif interaction.user.id != players_turn:
                await interaction.response.send_message(content=f"It's <@{players_turn}>'s turn!", ephemeral=True)
                continue

            if time.time() - player_info[players_turn]['time'] > 90:
                await interaction.response.defer()
                return -2, interaction

            await interaction.response.defer()
            if interaction.data['custom_id'] == 'back_bt':
                return 0, interaction

            if interaction.data['custom_id'] == 'use_bt':
                code, text = await use_item_screen(interaction, player_info)
                if text:
                    logs.appendleft(f"**{boss_info['turn']}|** " + text)

                return code, interaction

            elif interaction.data['custom_id'] == 'swap_bt':
                interaction.message.author = player_info[players_turn]['user']
                # noinspection PyTupleAssignmentBalance
                pickaxe, weapon, helmet, chest = await val_equipment(interaction.channel, interaction.user, 'val eq w',
                                                                     from_command=True,
                                                                     start_time_cmd=player_info[players_turn]['time'],
                                                                     slash_command=interaction)

                if pickaxe == -1:
                    return -2, interaction

                player_info[players_turn]['pickaxe'] = pickaxe
                player_info[players_turn]['weapon'] = weapon
                player_info[players_turn]['helmet'] = helmet
                player_info[players_turn]['chest'] = chest
                player_info[players_turn]['def'] = HELMETS[helmet]['def'] + ARMORS[chest]['def'] + \
                                                   player_info[players_turn]['agi'] // 3
                player_info[players_turn]['at'] = 2 * player_info[players_turn]['str'] * (
                        'normal' == WEAPONS[weapon]['type']) + int(
                    1.5 * player_info[players_turn]['agi'] * ('light' == WEAPONS[weapon]['type'])) + WEAPONS[weapon][
                                                      'at']
                return 1, interaction

            elif interaction.data['custom_id'] == 'flee_bt':
                return -1, interaction

            await interaction.message.edit(embed=embed, view=view)

        else:
            await interaction.message.edit(view=view)
            edited_button = True


async def use_item_screen(interaction, player_info):
    edited_message = False

    players_turn = interaction.user.id
    view = discord.ui.View()
    view.add_item(discord.ui.Button(emoji='⬆', style=discord.ButtonStyle.grey, custom_id='up_ui', row=1))

    view.add_item(
        discord.ui.Button(label='Use', emoji=EMOJIS['heal'], style=discord.ButtonStyle.blurple, custom_id='use_ui',
                          row=1))
    view.add_item(
        discord.ui.Button(label='Info', emoji='ℹ', style=discord.ButtonStyle.blurple, custom_id='info_ui', row=1))

    view.add_item(discord.ui.Button(emoji='⬇', style=discord.ButtonStyle.grey, custom_id='down_ui', row=2))
    view.add_item(discord.ui.Button(label='Back', emoji='⬅', style=discord.ButtonStyle.red, custom_id='back_ui', row=2))

    inventory = get_full_inventory_dict(players_turn)
    useful_items = []

    for item in inventory:
        if inventory[item] and 'heal_power' in ITEMS[item]:
            useful_items.append((item, inventory[item]))

    def check(inter):
        return inter.message.id == interaction.message.id

    embed = discord.Embed(description='', colour=ZONES[player_info[players_turn]['zone']]['color'])
    embed.set_author(name=f"{player_info[players_turn]['user'].name}'s inventory",
                     icon_url=player_info[players_turn]['user'].avatar)
    embed.set_footer(text="Only items that have effects will show up here!")

    current_index = 0
    info_screen = False
    while True:
        if edited_message:
            try:
                interaction = await bot.wait_for('interaction', timeout=90, check=check)
            except asyncio.TimeoutError:
                return -2, ''

            if interaction.user.id not in player_info:
                await interaction.response.send_message(
                    content="This is not your battle! Use `val battle` to start one yourself!", ephemeral=True)
                continue
            elif interaction.user.id != players_turn:
                await interaction.response.send_message(content=f"It's <@{players_turn}>'s turn!", ephemeral=True)
                continue

            if time.time() - player_info[players_turn]['time'] > 90:
                await interaction.response.defer()
                return -2, ''

            await interaction.response.defer()

            if interaction.data['custom_id'] == 'up_ui':
                current_index -= 1
                if current_index < 0:
                    current_index = len(useful_items) - 1

            elif interaction.data['custom_id'] == 'down_ui':
                current_index += 1
                if current_index >= len(useful_items):
                    current_index = 0

            elif interaction.data['custom_id'] == 'info_ui':
                info_screen = True

            elif interaction.data['custom_id'] == 'use_ui':
                if not useful_items:
                    continue
                return 1, use_item(player_info, interaction.user.id, useful_items[current_index][0],
                                   useful_items[current_index][1])

            elif interaction.data['custom_id'] == 'back_ui':
                if info_screen:
                    info_screen = False
                    view = discord.ui.View()
                    view.add_item(
                        discord.ui.Button(emoji='⬆', style=discord.ButtonStyle.grey, custom_id='up_ui', row=1))

                    view.add_item(
                        discord.ui.Button(label='Use', emoji=EMOJIS['heal'], style=discord.ButtonStyle.blurple,
                                          custom_id='use_ui',
                                          row=1))
                    view.add_item(discord.ui.Button(label='Info', emoji='ℹ', style=discord.ButtonStyle.blurple,
                                                    custom_id='info_ui', row=1))

                    view.add_item(
                        discord.ui.Button(emoji='⬇', style=discord.ButtonStyle.grey, custom_id='down_ui', row=2))
                    view.add_item(
                        discord.ui.Button(label='Back', emoji='⬅', style=discord.ButtonStyle.red, custom_id='back_ui',
                                          row=2))

                    embed = discord.Embed(description='', colour=ZONES[player_info[players_turn]['zone']]['color'])
                    embed.set_author(name=f"{player_info[players_turn]['user'].name}'s inventory",
                                     icon_url=player_info[players_turn]['user'].avatar)
                    embed.set_footer(text="Only items that have effects will show up here!")

                else:
                    return 0, ''

        if info_screen:
            interaction.message.author = player_info[players_turn]['user']
            embed = await val_help(interaction.channel, interaction.user,
                                   f"val help {ITEMS[useful_items[current_index][0]]['name'].lower()}",
                                   return_embed=True)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label='Use', emoji=EMOJIS['heal'],
                                            style=discord.ButtonStyle.blurple, custom_id='use_ui', row=1))
            view.add_item(discord.ui.Button(label='Back', emoji='⬅',
                                            style=discord.ButtonStyle.red, custom_id='back_ui', row=1))

        else:
            embed.description = f"**Zone {int_to_roman(player_info[players_turn]['zone'])} items:**\n\n"

            if not useful_items:
                embed.description += "You don't have any item from this zone that can be used!"

            else:
                for i, item in enumerate(useful_items):
                    if i == current_index:
                        embed.description += f"__{ITEMS[item[0]]['emoji']} **{ITEMS[item[0]]['name']}:** {item[1]}__ ⬅\n"
                    else:
                        embed.description += f"{ITEMS[item[0]]['emoji']} **{ITEMS[item[0]]['name']}:** {item[1]}\n"

        if not edited_message:
            await interaction.message.edit(view=view, embed=embed)
            edited_message = True
        else:
            await interaction.message.edit(view=view, embed=embed)


async def val_crates(channel: discord.TextChannel,
                     author: discord.User,
                     interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    embed = discord.Embed(colour=0x962f27, description="")
    embed.set_author(name=f"{author.name}'s info", icon_url=author.avatar)
    embed.set_footer(text="Open crates using [val open <crate name>]")

    embed.description = f"""
Crates are rewards obtained mainly from winning `battle`.
They contain resources based on the `zone` you open them in.

{get_area_crate_rewards(1)}\

> **🎁 Crates:**

**{CRATES[1]['emoji']} {CRATES[1]['name']}: up to 40 items**
**{CRATES[2]['emoji']} {CRATES[2]['name']}: up to 65 items**
**{CRATES[3]['emoji']} {CRATES[3]['name']}: up to 130 items**
**{CRATES[4]['emoji']} {CRATES[4]['name']}: up to 230 items**
**{CRATES[5]['emoji']} {CRATES[5]['name']}: up to ??? items**
**{CRATES[6]['emoji']} {CRATES[6]['name']}: up to ??? items**
**{CRATES[7]['emoji']} {CRATES[7]['name']}: up to ??? items**
"""

    if interaction and interaction.command:
        await interaction.edit_original_response(embed=embed)
    else:
        await channel.send(embed=embed)


async def val_open(channel: discord.TextChannel,
                   author: discord.User,
                   command: str,
                   interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    if not interaction:
        crate_amount = 1
        parameters = command.split()[2:]
        if not parameters:
            await send_response(content=
                                f"{author.mention} What are you trying to do? Correct usage: `val open <crate name> <amount>`")
            return

        if parameters[-1].isnumeric():
            crate_amount = int(parameters[-1])
            parameters.pop()

        given_crate_name = ' '.join(parameters)
    else:
        given_crate_name = ' '.join(interaction.data['options'][0]['value'].split())
        if len(interaction.data['options']) > 1:
            crate_amount = interaction.data['options'][1]['value']
        else:
            crate_amount = 1

    if crate_amount < 1:
        await send_response(content=f"{author.mention} The amount of crates opened must be at least 1")
        return

    crate_id = 0

    if given_crate_name in ('w', 'wooden', 'wooden crate'):
        crate_id = 1
    elif given_crate_name in ('m', 'metal', 'metal crate'):
        crate_id = 2
    elif given_crate_name in ('g', 'gold', 'gold crate'):
        crate_id = 3
    elif given_crate_name in ('c', 'cobalt', 'cobalt crate'):
        crate_id = 4
    elif given_crate_name in ('e', 'emerald', 'emerald crate'):
        crate_id = 5
    elif given_crate_name in ('r', 'ruby', 'ruby crate'):
        crate_id = 6
    elif given_crate_name in ('p', 'pogtanium', 'pogtanium crate'):
        crate_id = 7

    if not crate_id:
        await send_response(content=
                            f"{author.mention} What crate are you trying to open? Check `val crates` again!")
        return

    if crate_id > 4:
        await send_response(content=f"{author.mention} Cant open this yet (WORK IN PROGRESS)!")
        return

    crates = get_user_crates(author.id)
    if crate_id not in crates:
        await send_response(content=
                            f"{author.mention} You don't have any {CRATES[crate_id]['emoji']} **{CRATES[crate_id]['name']}** in your inventory.")
        return

    if crates[crate_id] < crate_amount:
        await send_response(content=
                            f"{author.mention} You don't have that many {CRATES[crate_id]['emoji']} **{CRATES[crate_id]['name']}s** in your inventory!")
        return
    if crate_amount > 5000:
        await send_response(content=f"{author.mention} You can't open more than **5000 crates** at once!")
        return

    embed = discord.Embed(colour=ZONES[area]['color'], description="")
    embed.set_author(name=f"{author.name}'s crate", icon_url=author.avatar)
    emoji = bot.get_emoji(int(CRATES[crate_id]['emoji'].split(':')[2][:-1]))
    embed.set_thumbnail(url=emoji.url)

    rewards = {'amount': 0}
    total_items = CRATES[crate_id]['min_items'] * crate_amount
    rarity_list = [rarity for rarity in CRATE_ITEMS_PER_AREA[area] if
                   CRATE_ITEMS_PER_AREA[area][rarity] and rarity in CRATES[crate_id]]

    while rewards['amount'] < total_items:
        await asyncio.sleep(0)
        item = 0
        for rarity in rarity_list:
            if random_float(0, 99) < CRATES[crate_id][rarity][0]:
                item = random.choice(CRATE_ITEMS_PER_AREA[area][rarity])
                amount = random.randint(CRATES[crate_id][rarity][1], CRATES[crate_id][rarity][2])
                rewards['amount'] += amount

                if item in rewards:
                    rewards[item] += amount
                else:
                    rewards[item] = amount

        if not item:
            item = random.choice(CRATE_ITEMS_PER_AREA[area]['common'])
            amount = random.randint(CRATES[crate_id]['common'][1], CRATES[crate_id]['common'][2])
            rewards['amount'] += amount

            if item in rewards:
                rewards[item] += amount
            else:
                rewards[item] = amount

    del rewards['amount']
    text = f"""**You** opened {'a' if crate_amount == 1 else f"**{crate_amount}**"} {CRATES[crate_id]['emoji']} **{CRATES[crate_id]['name']}{'s' if crate_amount > 1 else ''}**!\n> **Rewards:**\n\n"""
    remove_crates(author.id, crate_id, crate_amount)
    for item_id in rewards:
        text += f"{ITEMS[item_id]['emoji']} **{ITEMS[item_id]['name']}:** {rewards[item_id]}\n"

        add_item(author.id, item_id, rewards[item_id])

    embed.description = text

    await send_response(embed=embed)


def get_run_cmd_view():
    view = discord.ui.View()
    select = discord.ui.Select(custom_id='command', placeholder="Use another command", min_values=1)
    select.options = [
        discord.SelectOption(label='Mine', emoji="⛏",
                             description="Mine for resources"),
        discord.SelectOption(label='Seek', emoji='🗡',
                             description='Seek enemies to defeat'),
        discord.SelectOption(label='Cooldowns', emoji='⏱', description='View your cooldowns'),
        discord.SelectOption(label='Inventory', emoji='🎒', description='View your inventory'),
        discord.SelectOption(label='Profile', emoji=EMOJIS['hp'], description='View your profile'),
        discord.SelectOption(label='Recipes', emoji="📃", description="View available recipes")]

    view.add_item(select)
    view.stop()
    return view


ZONE_REQUIREMENTS = {
    1: {'items': {1: 1600, 3: 150, 5: 300},
        'text': f"**You** explored around **{random.choice(ZONES[1]['emoji'])} The Forest** for a while, and you came across a great ravine!\n"
                "Looks like there was a bridge for crossing over it, but it was ruined long ago... \n"
                "On the other side of the ravine there is a desert.\n"
                "Perhaps you can rebuild the bridge if you have the necessary resources and skills: \n\n",
        'text2': "Once you rebuild the bridge you can't get back the resources.",

        'text_done': "**You** have managed to repair the bridge!\nYou where getting ready to cross, but as soon as you "
                     f"get close to it a {BOSSES[1]['mud_golem_spawner']} **MUD GOLEM SPAWNER** appears! Looks like you angered the forest's spirits..."
                     f"\nUse `/progress` to enter this fight and reach `zone II`! It's recommended to have some party members, this fight won't be easy!"
                     f"\n\n**BRIDGE COMPLETED ✅**",
        'req_not_done_warning': "because they didn't rebuild their bridge!",
        'battle_against': f"{BOSSES[1]['mud_golem_spawner']} **MUD GOLEM SPAWNER**"}
}


async def val_explore(channel: discord.TextChannel,
                      author: discord.User,
                      interaction: discord.Interaction = None):
    area = await get_player_area(channel, author)
    if not area:
        return

    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    inventory = get_full_inventory_dict(author.id)
    zone_status = get_zone_status(author.id, area)
    is_ready = True
    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s findings", icon_url=author.avatar)

    if not zone_status:
        items_collected_text = ''
        for item_req, amount_req in ZONE_REQUIREMENTS[area]['items'].items():
            if inventory[item_req] >= amount_req:
                items_collected_text += f"- {amount_req}/{amount_req} {ITEMS[item_req]['emoji']} **{ITEMS[item_req]['name']}** ✅\n"
            else:
                is_ready = False
                items_collected_text += f"- {inventory[item_req]}/{amount_req} {ITEMS[item_req]['emoji']} **{ITEMS[item_req]['name']}\n**"
        embed.description = f"""{ZONE_REQUIREMENTS[area]['text']}{items_collected_text}

{ZONE_REQUIREMENTS[area]['text2']}"""
    else:
        embed.description = f"""{ZONE_REQUIREMENTS[area]['text_done']}"""

    embed.set_footer(text="You can feel a dark presence around you...")
    embed.set_thumbnail(url=random.choice(ZONES[area]['image_link']))
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Rebuild', emoji='🔨', custom_id=f'rebuild_zone{author.id}',
                                    disabled=not is_ready or zone_status))

    await send_response(embed=embed, view=view)


async def val_reconstruct(channel, author, interaction: discord.Interaction):
    if author.id != int(interaction.data['custom_id'][12:]):
        await channel.send(f"{author.mention} This is not your command! Use `/explore` to see this!")
        return

    area = await get_player_area(channel, author)
    inventory = get_full_inventory_dict(author.id)
    for item_req, amount_req in ZONE_REQUIREMENTS[area]['items'].items():
        if inventory[item_req] < amount_req:
            await channel.send(
                f"{author.mention} Looks like you don't have the required resources anymore, check `/explore` again!")
            return

    for item_req, amount_req in ZONE_REQUIREMENTS[area]['items'].items():
        remove_item(author.id, item_req, amount_req)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label='Rebuild', emoji='🔨', disabled=True))

    embed = discord.Embed(colour=ZONES[area]['color'])
    embed.set_author(name=f"{author.name}'s findings", icon_url=author.avatar)
    embed.description = f"""{ZONE_REQUIREMENTS[area]['text_done']}"""
    embed.set_footer(text="You can feel a dark presence around you...")
    embed.set_thumbnail(url=random.choice(ZONES[area]['image_link']))

    set_zone_req_complete(author.id, area)
    await interaction.edit_original_response(embed=embed, view=view)


async def val_move(channel: discord.TextChannel,
                   author: discord.User,
                   command: str,
                   interaction: discord.Interaction = None):
    if interaction and interaction.command:
        send_response = interaction.edit_original_response
    else:
        send_response = channel.send

    zone, max_zone = get_zone_and_max(author.id)

    zone_to_move = 0
    if not interaction:
        parameters = command.split()[2:]
        if not parameters:
            await send_response(
                content=f"<@{author.id}>, please specify the zone to move to. Correct usage: `val move [zone_number]`.")
            return

        if parameters[-1].replace('-', '').isnumeric():
            zone_to_move = int(parameters[-1])

        if not zone_to_move:
            await send_response(
                content=f"<@{author.id}>, please specify the zone to move to. Correct usage: `val move [zone_number]`.")
            return
    else:
        zone_to_move = interaction.data['options'][0]['value']

    if zone_to_move > max_zone:
        await send_response(content=f"<@{author.id}>, you can't move to a zone higher than your max zone!")
        return

    if zone_to_move == zone:
        await send_response(content=f"<@{author.id}>, you are already in `zone {int_to_roman(zone_to_move)}`!")
        return

    if zone_to_move <= 0:
        await send_response(
            content=f"<@{author.id}>,y̶o̷u̷ ̴c̶a̵n̷'̷t̸ ̸m̵o̵v̵e̴ ̴t̸o̷ `̸z̶o̸n̶e̴ ̴-{int_to_roman(abs(zone_to_move))}` y̷e̴t̵?")
        return

    set_current_zone(author.id, zone_to_move)

    await send_response(content=f"<@{author.id}>, moved to `zone {int_to_roman(zone_to_move)}`!")


class TestCommand(discord.ui.View):
    def __init__(self, channel, author, *, timeout=180):
        self.count = 0
        self.channel = channel
        self.author = author
        self.message = None
        super().__init__(timeout=timeout)

    async def send_initial_message(self):
        self.message = await self.channel.send(f"{self.count}", view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)

    @discord.ui.button(emoji="➕", label='1', style=discord.ButtonStyle.green)
    async def button_add_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(f"{interaction.user.mention}, this is not your command!", ephemeral=True)
            return

        self.count += 1

        await interaction.response.edit_message(content=f"{self.count}")
