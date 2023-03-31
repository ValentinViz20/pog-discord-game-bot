from slash_commands import *


@bot.event
async def on_ready():
    VIEWS['base_select'] = get_run_cmd_view()
    # await command_tree.sync(guild=discord.Object(id=1013730028615372800))
    print(f"Connected in bot {bot.user}")
    initialize_db()


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if ('custom_id' in interaction.data and (interaction.data['custom_id'] == 'mine_command' or
        (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Mine")) or
        (interaction.command and interaction.command.name == 'mine')):
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        DATA_CACHE[interaction.user.id]['cmd'] = 1
        embed_view = await val_mine(interaction.channel, interaction.user, interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

        if embed_view:
            await asyncio.sleep(19.5)
            await interaction.channel.send(f"<@{interaction.user.id}> You are ready to **MINE** again!",
                                           view=embed_view)
            return

    elif (('custom_id' in interaction.data and (interaction.data['custom_id'] == 'seek_command' or
         (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Seek"))) or
            (interaction.command and interaction.command.name == 'seek')):
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        DATA_CACHE[interaction.user.id]['cmd'] = 2

        embed_view = await val_seek(interaction.channel, interaction.user, interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

        if embed_view:
            await asyncio.sleep(59.5)
            await interaction.channel.send(f"<@{interaction.user.id}> You are ready to **SEEK** again!",
                                           view=embed_view)
            return

    elif (('custom_id' in interaction.data and interaction.data['custom_id'] == 'heal_command') or
         (interaction.command and interaction.command.name == 'heal')):
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        DATA_CACHE[interaction.user.id]['cmd'] = 18
        await val_heal(interaction.channel, interaction.user, command='', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif (('custom_id' in interaction.data and interaction.data['custom_id'].startswith('tspend_command')) or
         (interaction.command and interaction.command.name == 'traits')):

        if 'custom_id' in interaction.data and interaction.data['custom_id'][14:] and interaction.user.id != int(interaction.data['custom_id'][14:]):
            await interaction.response.send_message(
                f"<@{interaction.user.id}>, this is not your profile! Use `val p` to check if you have unspent trait points!", ephemeral=True)
            return

        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        await val_traits(interaction.channel, interaction.user,
                         interaction_command=interaction if not interaction.command else None,
                         assign_screen=not interaction.command and interaction.data['custom_id'][14:],
                         slash_command=interaction)

    elif 'custom_id' in interaction.data and interaction.data['custom_id'].startswith('inventory'):
        if not interaction.data['custom_id'].endswith(str(interaction.user.id)):
            await interaction.response.send_message(content=f"{interaction.user.mention}, that's not your command!\n"
                                                            f"Use `/inventory [player] [zone]` to view their items!",
                                                    ephemeral=True)
            return

        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 8
        await val_inventory(interaction.channel, interaction.user, '',  [], interaction=interaction,
                            show_zone=int(interaction.data['values'][0]))
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif (('custom_id' in interaction.data and (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Inventory")) or
            (interaction.command and interaction.command.name == 'inventory')):
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 8
        await val_inventory(interaction.channel, interaction.user, '', [], interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif (('custom_id' in interaction.data and (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Profile")) or
            (interaction.command and interaction.command.name == 'profile')):
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 7
        await val_profile(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'help':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 4
        await val_help(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif ((interaction.command and interaction.command.name == 'cooldowns') or
          ('custom_id' in interaction.data and (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Cooldowns"))):
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 5
        await val_cooldown(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'ready':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 6
        await val_ready(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif 'custom_id' in interaction.data and interaction.data['custom_id'].startswith('rebuild_zone'):
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 19
        await val_reconstruct(interaction.channel, interaction.user, interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'craft':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 10
        await val_craft(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif 'custom_id' in interaction.data and interaction.data['custom_id'] == 'equipment_command':
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        await val_equipment(interaction.channel, interaction.user, '', slash_command=interaction)

    elif (interaction.command and interaction.command.name == 'recipes') or ('custom_id' in interaction.data and (interaction.data['custom_id'] == 'command' and interaction.data['values'][0] == "Recipes")):
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        await val_recipes(interaction.channel, interaction.user, '', interaction=interaction)

    elif interaction.command and interaction.command.name == 'build':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 9
        await val_build(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'crates':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 12
        await val_crates(interaction.channel, interaction.user, interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'destroy':
        if await is_in_command_interaction(interaction):
            return
        await interaction.response.defer()

        DATA_CACHE[interaction.user.id]['cmd'] = 11
        await val_destory(interaction.channel, interaction.user, '', interaction=interaction)
        DATA_CACHE[interaction.user.id]['cmd'] = 0

    elif interaction.command and interaction.command.name == 'house':
        if await is_in_command_interaction(interaction):
            return

        await interaction.response.defer()
        await val_house(interaction.channel, interaction.user, interaction=interaction)

    elif not interaction.command:
        if interaction.message.id in INTERACTION_BUCKET:
            INTERACTION_BUCKET[interaction.message.id].append(interaction)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.content == f"<@{bot.user.id}>":
        await message.channel.send("Hello, I am online. My prefix is `val`, say `val begin` to start playing!")
        return

    command = ' '.join(message.content.lower().split()) + ' '

    if command.startswith('fix me'):
        DATA_CACHE[message.author.id]['cmd'] = 0
        await message.channel.send("Done. Please report the way you got stuck!!!")
        return

    # spam protection ========================================================================================
    if not command.startswith(('val ', f"<@{bot.user.id}> ")) or await is_in_command(message.channel, message.author.id):
        return

    # Commands =========================================================================================================
    if command.startswith(('val help ', f"<@{bot.user.id}> help ",
                           'val h ', f"<@{bot.user.id}> h ")):
        DATA_CACHE[message.author.id]['cmd'] = 4
        await val_help(message.channel, message.author, command)

    elif command.startswith(('val cd ', f"<@{bot.user.id}> cd ", 'val cooldown ', f"<@{bot.user.id}> cooldown ")):
        DATA_CACHE[message.author.id]['cmd'] = 5
        await val_cooldown(message.channel, message.author, command)

    elif command.startswith(('val rd ', f"<@{bot.user.id}> rd ", 'val ready ', f"<@{bot.user.id}> ready ")):
        DATA_CACHE[message.author.id]['cmd'] = 6
        await val_ready(message.channel, message.author, command)

    elif command.startswith(('val p ', f"<@{bot.user.id}> p ", 'val profile ', f"<@{bot.user.id}> profile ")):
        DATA_CACHE[message.author.id]['cmd'] = 7
        await val_profile(message.channel, message.author, command)

    elif command.startswith(('val mine ', f"<@{bot.user.id}> mine ")):
        DATA_CACHE[message.author.id]['cmd'] = 1
        embed_view = await val_mine(message.channel, message.author)
        DATA_CACHE[message.author.id]['cmd'] = 0

        if embed_view:
            await asyncio.sleep(19.5)
            await message.channel.send(f"<@{message.author.id}> You are ready to **MINE** again!", view=embed_view)

        return
    # SEEK ============================================================================================================
    elif command.startswith(('val seek ', f"<@{bot.user.id}> seek ")):
        DATA_CACHE[message.author.id]['cmd'] = 2
        embed_view = await val_seek(message.channel, message.author)
        DATA_CACHE[message.author.id]['cmd'] = 0

        if embed_view:
            await asyncio.sleep(59.5)
            await message.channel.send(f"<@{message.author.id}> You are ready to **SEEK** again!", view=embed_view)

        return

    elif command.startswith(('val inventory ', f"<@{bot.user.id}> inventory ",
                             'val inv ', f"<@{bot.user.id}> inv ",
                             'val i ', f"<@{bot.user.id}> i ")):
        DATA_CACHE[message.author.id]['cmd'] = 8
        await val_inventory(message.channel, message.author, command, message.mentions)

    elif command.startswith(('val house ', f"<@{bot.user.id}> house ")):
        await val_house(message.channel, message.author)

    elif command.startswith(('val build ', f"<@{bot.user.id}> build ")):
        DATA_CACHE[message.author.id]['cmd'] = 9
        await val_build(message.channel, message.author, command)

    elif command.startswith(('val recipes ', f"<@{bot.user.id}> recipes ")):
        await val_recipes(message.channel, message.author, command)

    elif command.startswith(('val craft ', f"<@{bot.user.id}> craft ")):
        DATA_CACHE[message.author.id]['cmd'] = 10
        await val_craft(message.channel, message.author, command)

    elif command.startswith(('val traits ', f"<@{bot.user.id}> traits ")):
        if await is_in_command(message.channel, message.author.id):
            return
        await val_traits(message.channel, message.author)

    elif command.startswith(('val destroy ', f"<@{bot.user.id}> destroy ")):
        DATA_CACHE[message.author.id]['cmd'] = 11
        await val_destory(message.channel, message.author, command)

    elif command.startswith(('val crates ', f"<@{bot.user.id}> crates ")):
        DATA_CACHE[message.author.id]['cmd'] = 12
        await val_crates(message.channel, message.author)

    elif command.startswith(('val open ', f"<@{bot.user.id}> open ")):
        DATA_CACHE[message.author.id]['cmd'] = 13
        await val_open(message.channel, message.author, command)

    elif command.startswith(('val progress ', f"<@{bot.user.id}> progress ")):
        await val_battle(message.channel, message.author, message.mentions, zone_boss=1)

    elif command.startswith(('val use ', f"<@{bot.user.id}> use ")):
        DATA_CACHE[message.author.id]['cmd'] = 14
        await val_use(message.channel, message.author, command)

    elif command.startswith(('val equip ', f"<@{bot.user.id}> equip ")):
        DATA_CACHE[message.author.id]['cmd'] = 15
        await val_equip(message.channel, message.author, command)

    elif command.startswith(('val add fuel ', f"<@{bot.user.id}> add fuel ")):
        DATA_CACHE[message.author.id]['cmd'] = 16
        await val_add_fuel(message.channel, message.author, command)

    elif command.startswith(('val eq ', f"<@{bot.user.id}> eq ",
                             'val equipment ', f"<@{bot.user.id}> equipment ")):
        await val_equipment(message.channel, message.author, command)

    elif command.startswith(('val remove fuel ', f"<@{bot.user.id}> remove fuel ")):
        DATA_CACHE[message.author.id]['cmd'] = 17
        await val_remove_fuel(message.channel, message.author, command)

    elif command.startswith(('val heal ', f"<@{bot.user.id}> heal ")):
        DATA_CACHE[message.author.id]['cmd'] = 18
        await val_heal(message.channel, message.author, command)

    elif command.startswith(('val move ', f"<@{bot.user.id}> move ")):
        await val_move(message.channel, message.author, command)

    elif command.startswith(('val explore ', f"<@{bot.user.id}> explore ")):
        await val_explore(message.channel, message.author)

    elif command.startswith(('val battle ', f"<@{bot.user.id}> battle ",
                             'val bt ', f"<@{bot.user.id}> bt ")):
        DATA_CACHE[message.author.id]['cmd'] = 3
        await val_battle(message.channel, message.author, message.mentions)

    elif command.startswith(('val nc ', f"<@{bot.user.id}> nc ")) and message.author.id == NECROMANCER_ID:
        await val_nc(message, command)

    elif command.startswith(('val reset all my progress ', f"<@{bot.user.id}> reset all my progress ")):
        reset_progress(message.author.id)
        await message.channel.send("I have erased you from my memory. All of your progress was reset.")

    elif command.startswith(('val begin', f"<@{bot.user.id}> begin ")):
        await add_player_first_time(message)
        return

    elif command.startswith(('val test', f"<@{bot.user.id}> test ")):
        test_command = TestCommand(message.channel, message.author, timeout=15)
        await test_command.send_initial_message()
        return

    DATA_CACHE[message.author.id]['cmd'] = 0


if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    bot.run()
