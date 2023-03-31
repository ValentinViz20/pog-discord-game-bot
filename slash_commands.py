import enum

from game_commands import *


@command_tree.command(name='mine', description="", guild=discord.Object(id=1013730028615372800))
async def mine(interaction: discord.Interaction):
    pass


@command_tree.command(name='inventory', description='Check your inventory', guild=discord.Object(id=1013730028615372800))
async def inventory(interaction: discord.Interaction, user: discord.User = None):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    mentions = []
    if user:
        mentions.append(user)

    DATA_CACHE[interaction.user.id]['cmd'] = 8
    await val_inventory(interaction.channel, interaction.user, '', mentions, interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='profile', description='Check your profile', guild=discord.Object(id=1013730028615372800))
async def profile(interaction: discord.Interaction, user: discord.User = None):
    pass


@command_tree.command(name='help', description='Find help for commands or other', guild=discord.Object(id=1013730028615372800))
async def help(interaction: discord.Interaction, topic: str = None):
    pass


@command_tree.command(name='seek', description='Seek enemies to defeat', guild=discord.Object(id=1013730028615372800))
async def seek(interaction: discord.Interaction):
    pass


@command_tree.command(name='heal', description='Use healing items to replenish health', guild=discord.Object(id=1013730028615372800))
async def seek(interaction: discord.Interaction, full: bool = False):
    pass


@command_tree.command(name='cooldowns', description='View the time left until you can use your commands', guild=discord.Object(id=1013730028615372800))
async def cooldowns(interaction: discord.Interaction, full: bool = False):
    pass


@command_tree.command(name='ready', description='View the commands ready to use', guild=discord.Object(id=1013730028615372800))
async def ready(interaction: discord.Interaction, full: bool = False):
    pass


@command_tree.command(name='house', description='View your house and the crafting stations inside', guild=discord.Object(id=1013730028615372800))
async def house(interaction: discord.Interaction):
    pass


@command_tree.command(name='craft', description='Craft items and equipment', guild=discord.Object(id=1013730028615372800))
async def craft(interaction: discord.Interaction, what_to_craft: str, amount: int = 1):
    pass


@command_tree.command(name='build', description='Build houses and crafting stations', guild=discord.Object(id=1013730028615372800))
async def build(interaction: discord.Interaction, what_to_build: str):
    pass


class RecipeCategories(enum.Enum):
    pickaxes = 'p'
    weapons = 'w'
    items = 'i'
    builds = 'b'
    armors = 'a'


@command_tree.command(name='recipes', description='View the recipes for anything in the game', guild=discord.Object(id=1013730028615372800))
async def recipes(interaction: discord.Interaction, category: RecipeCategories = RecipeCategories.pickaxes, zone: int = 0):
    pass


@command_tree.command(name='traits', description='View, assign or remove your traits', guild=discord.Object(id=1013730028615372800))
async def traits(interaction: discord.Interaction):
    pass


@command_tree.command(name='destroy', description='Destroy a crafting station', guild=discord.Object(id=1013730028615372800))
async def destroy(interaction: discord.Interaction, station_to_destroy: str, slot: int = 0):
    pass


@command_tree.command(name='crates', description='View all the crate types and what you can find inside them', guild=discord.Object(id=1013730028615372800))
async def crates(interaction: discord.Interaction):
    pass


@command_tree.command(name='use', description='Use an item', guild=discord.Object(id=1013730028615372800))
async def use(interaction: discord.Interaction, item_to_use: str, amount: int = 1):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 14
    await val_use(interaction.channel, interaction.user, '', interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='equip', description='Equip another pickaxe, weapon or helmet', guild=discord.Object(id=1013730028615372800))
async def equip(interaction: discord.Interaction, item_to_equip: str):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 15
    await val_equip(interaction.channel, interaction.user, '', interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='add-fuel', description='Add fuel to one of your furnaces', guild=discord.Object(id=1013730028615372800))
async def add_fuel(interaction: discord.Interaction, item_to_add: str, amount: int = 1):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 16
    await val_add_fuel(interaction.channel, interaction.user, '', interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


class EquipmentCategories(enum.Enum):
    pickaxes = 'p'
    weapons = 'w'
    armors = 'a'
    helmets = 'h'


@command_tree.command(name='equipment', description='View and change your equipment', guild=discord.Object(id=1013730028615372800))
async def equipment(interaction: discord.Interaction, category: EquipmentCategories = EquipmentCategories.pickaxes):
    if await is_in_command_interaction(interaction):
        return

    await interaction.response.defer()
    await val_equipment(interaction.channel, interaction.user, '', slash_command=interaction)


@command_tree.command(name='battle', description='Battle strong enemies', guild=discord.Object(id=1013730028615372800))
async def battle(interaction: discord.Interaction, party_member1: discord.User = None, party_member2: discord.User = None):
    if await is_in_command_interaction(interaction):
        return

    mentions = []
    if party_member1:
        mentions.append(party_member1)
    if party_member2:
        mentions.append(party_member2)
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 3
    await val_battle(interaction.channel, interaction.user, mentions, interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='progress', description='Progress to the next zone', guild=discord.Object(id=1013730028615372800))
async def progress(interaction: discord.Interaction, party_member1: discord.User = None, party_member2: discord.User = None):
    if await is_in_command_interaction(interaction):
        return

    mentions = []
    if party_member1:
        mentions.append(party_member1)
    if party_member2:
        mentions.append(party_member2)
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 3
    await val_battle(interaction.channel, interaction.user, mentions, interaction=interaction, zone_boss=1)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='remove-fuel', description='Remove fuel from one of your furnaces', guild=discord.Object(id=1013730028615372800))
async def remove_fuel(interaction: discord.Interaction, amount_to_remove: int):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 17
    await val_remove_fuel(interaction.channel, interaction.user, '', interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0


@command_tree.command(name='explore', description='Explore the zone you are in', guild=discord.Object(id=1013730028615372800))
async def remove_fuel(interaction: discord.Interaction):
    if await is_in_command_interaction(interaction):
        return

    await interaction.response.defer()
    await val_explore(interaction.channel, interaction.user, interaction=interaction)


@command_tree.command(name='move', description='Move to another zone', guild=discord.Object(id=1013730028615372800))
async def move(interaction: discord.Interaction):
    if await is_in_command_interaction(interaction):
        return

    await interaction.response.defer()
    await val_move(interaction.channel, interaction.user, '', interaction=interaction)


@command_tree.command(name='open', description='Open your crates', guild=discord.Object(id=1013730028615372800))
@discord.app_commands.choices(crate=[
    discord.app_commands.Choice(name='Wooden Crate', value='w'),
    discord.app_commands.Choice(name='Metal Crate', value='m'),
    discord.app_commands.Choice(name='Gold Crate', value='g'),
    discord.app_commands.Choice(name='Cobalt Crate', value='c'),
    discord.app_commands.Choice(name='Emerald Crate', value='e'),
    discord.app_commands.Choice(name='Ruby Crate', value='r'),
    discord.app_commands.Choice(name='Pogtanium Crate', value='p'),
])
async def _open(interaction: discord.Interaction, crate: discord.app_commands.Choice[str], amount: int = 1):
    if await is_in_command_interaction(interaction):
        return
    await interaction.response.defer()

    DATA_CACHE[interaction.user.id]['cmd'] = 13
    await val_open(interaction.channel, interaction.user, '', interaction=interaction)
    DATA_CACHE[interaction.user.id]['cmd'] = 0

