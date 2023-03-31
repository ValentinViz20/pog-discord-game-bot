import random
import typing

import discord

from helper_functions import *

# https://discord.gg/dRsswJYeN7

ITEMS = {
    0: {'name': "None", 'emoji': None, 'smelt_time': 0, 'fuel_power': 0},
    1: {'name': "Dirt", 'emoji': "<:dirt_2:1014640604409511997>", 'zone': 1, 'command': 'mine', 'rarity': 1},
    2: {'name': "Clay", 'emoji': "<:clay:1014489863891992666>", 'zone': 1, 'command': 'mine', 'rarity': 1},
    3: {'name': "Log", 'emoji': "<:woodlog:1014460043007098981>", 'fuel_power': 3 * 60, 'zone': 1, 'command': 'mine',
        'rarity': 3},
    4: {'name': "Pumpkin", 'emoji': "<:pumpkin:1014428524490281022>", 'zone': 1, 'command': 'mine', 'rarity': 4},
    5: {'name': "Tree Branch", 'emoji': "<:tree_branch:1014428457918267453>", 'fuel_power': 60, 'zone': 1,
        'command': 'mine', 'rarity': 2},
    6: {'name': "Brick", 'emoji': "<:brick:1014881750834487446>", 'recipe': [(2, 5)], 'station': 2,
        'smelt_time': 90, 'zone': 1, 'rarity': 2},
    7: {'name': "Wolf Pelt", 'emoji': "<:wolf_pelt:1016601835487891508>", 'zone': 1, 'command': 'seek', 'rarity': 4},
    8: {'name': "Gel", 'emoji': "<:gel:1016600186459533423>", 'fuel_power': 5 * 60, 'zone': 1, 'command': 'seek',
        'rarity': 4},
    9: {'name': "Spooky Wood", 'emoji': "<:spooky_wood:1016603290391302154>", 'zone': 1, 'command': 'seek',
        'rarity': 5},
    10: {'name': "Leather", 'emoji': "<:leather:1016604337021128754>", 'recipe': [(7, 1)], 'smelt_time': 5 * 60,
         'zone': 1, 'rarity': 4},
    11: {'name': "Antlers", 'emoji': "<:antlers:1023928577877614602>", 'zone': 1, 'command': 'seek', 'rarity': 5},
    12: {'name': "Fruit", 'emoji': "<:fruit:1016679136405762150>", 'heal_power': 30, 'zone': 1, 'command': 'mine',
         'rarity': 1},
    13: {'name': "Pumpkin Pie", 'emoji': "<:pumpkin_pie:1016681257993781328>", 'heal_power': 150,
         'recipe': [(4, 1), (12, 3)], 'smelt_time': 20, 'zone': 1, 'rarity': 4, 'station': 2},
    14: {'name': "Book of Forgiveness", 'emoji': "<:book_1:1026849401894871111>", 'zone': 999,
         'effect': "Unassigns **ALL** traits points without without leveling you down. You can assign them back right after using the book.",
         'rarity': 6},

    15: {'name': "Glass Shard", 'emoji': "<:glass_shard:1026197930304082000>", 'zone': 2, 'rarity': 2,
         'recipe': [(16, 10)], 'station': 2, 'smelt_time': 60 * 2, },
    16: {'name': "Sand", 'emoji': "<:sand:1026875087401537556>", 'zone': 2, 'rarity': 1, 'command': 'mine'},
    17: {'name': "Prickly Pear", 'emoji': "<:cactus_fruit:1026875184466112573>", 'zone': 2, 'rarity': 1,
         'command': 'mine', 'heal_power': 50},
    18: {'name': "Copper Bar", 'emoji': "<:copper_bar:1026875164174065705>", 'zone': 4, 'rarity': 10,
         'recipe': [(19, 5)],
         'smelt_time': 60 * 5, 'station': 5},
    19: {'name': "Copper Ore", 'emoji': "<:copper_ore:1026875148374130782>", 'zone': 2, 'rarity': 4,
         'command': 'mine', 'station': 5, },
    20: {'name': "Cactus", 'emoji': "<:cactus:1026875199662063697>", 'zone': 1, 'rarity': 10, 'command': 'mine', },
    21: {'name': "Bones", 'emoji': "<:bones:1026875217332686848>", 'zone': 2, 'rarity': 10, 'command': 'mine', },
    22: {'name': "Mysterious Fragment", 'emoji': "<:misterious_fragment:1026875114555449395>", 'zone': 3, 'rarity': 10,
         'command': 'mine'},
    23: {'name': "Carapace", 'emoji': "<:carapace:1029351183313276958>", 'zone': 3, 'command': 'seek & battle',
         'rarity': 10},
}

SPECIAL_ITEMS = [14]

# rarity: (chance, min_items, max_items)
# 🟫 Common 1
# 🟦 Uncommon 2
# 🟨 Rare 3
# 🟧 Very Rare 4
# 🟩 Epic 5
# 🟥 Legendary 6
# Insane 7

CRATES = {
    1: {'name': 'Wooden Crate', 'emoji': '<:wooden_crate:1024625390788018188>',
        'common': (90, 20, 40), 'uncommon': (50, 1, 8), 'rare': (5, 1, 4), 'very rare': (15, 1, 1),
        'min_items': 30},

    2: {'name': 'Metal Crate', 'emoji': '<:metal_crate:1024709352994656346>',
        'common': (99, 30, 50), 'uncommon': (40, 1, 17), 'rare': (15, 1, 6), 'very rare': (45, 1, 1),
        'epic': (0.3, 1, 1),
        'min_items': 40},

    3: {'name': 'Gold Crate', 'emoji': '<:gold_crate:1024673639796326401>',
        'common': (99, 50, 100), 'uncommon': (80, 10, 20), 'rare': (50, 10, 25), 'very rare': (70, 1, 2),
        'epic': (1, 1, 1),
        'legendary': (0.1, 1, 1),
        'min_items': 75},

    4: {'name': 'Cobalt Crate', 'emoji': '<:azurite_crate:1024947385341841418>',
        'common': (99, 100, 180), 'uncommon': (90, 30, 40), 'rare': (70, 20, 60), 'very rare': (90, 2, 4),
        'epic': (2, 1, 1),
        'legendary': (1, 1, 1), 'insane': (0.1, 1, 1),
        'min_items': 150},

    5: {'name': 'Emerald Crate', 'emoji': '<:emerald_crate:1024661259355963462>'},
    6: {'name': 'Ruby Crate', 'emoji': '<:ruby_crate:1024664349719154688>'},
    7: {'name': 'Pogtanium Crate', 'emoji': "<a:pogtanium_crate:1024941840883011634>"}
}

ZONES = {
    1: {'name': "The Forest",
        'emoji': ["<:forest_zone:1015956274724229170>", "<:forest_zone2:1015973514295115836>",
                  '<:forest3:1025399824780120216>',
                  "<:forest4:1025400110206697513>"],
        'image_link': ["https://cdn.discordapp.com/attachments/892766502325997568/1015955898381901874/forest.jpg",
                       "https://cdn.discordapp.com/attachments/1014424926519820301/1015973348251021392/tempsnip.png",
                       "https://cdn.discordapp.com/attachments/1021824174563536990/1025399656945045554/unknown.png",
                       "https://cdn.discordapp.com/attachments/892766502325997568/1023162403736801380/dark_forest.jpg"],
        'color': 0x962f27},

    2: {'name': "The Desert",
        'emoji': ["<:desert1:1026894779033849947>", "<:desert2:1026895118772478052>"],
        'image_link': ["https://cdn.discordapp.com/emojis/1026894779033849947.webp?size=128&quality=lossless",
                       "https://cdn.discordapp.com/emojis/1026895118772478052.webp?size=128&quality=lossless"],
        'color': 0xebb134}
}

EMOJIS = {
    'trait': '<:trait_icon:1024595811348250725>',
    'hp': '<:heart:1024599176778092595>',
    'def': '<:defense:1018830920616251462>',
    'at': '<:at:1019224859651350609>',
    'heal': '<:heal:1019542172569174057>',
    'mana': '<:mana:1023125856673075200>',

    'rbl': '<:red_bar_left:1022428249734783016>',
    'rbm': '<:red_bar_middle:1022428155916587078>',
    'rbr': '<:red_bar_right:1022428110173511710>',

    'gbl': '<:gbl2:1022438808207249418>',
    'gbm': '<:gbm2:1022438773574864947>',
    'gbr': '<:gbr2:1022438724056911882>',

    'ebl': '<:empty_bar_left:1022435957326233600>',
    'ebm': '<:empty_bar_middle:1022436015786442832>',
    'ebr': '<:empty_bar_right:1022436070173970432>'
}

PICKAXES = {
    0: {'name': "Hands",
        'emoji': "<:hands:1014776207738425437>",
        'station': 0,
        'min_items': 1,
        'max_items': 1,
        'power': 0,
        'zone': 1},

    1: {'name': "Dirt Pickaxe",
        'emoji': "<:dirt_pickaxe:1014829520316022824>",
        'station': 1,
        'recipe': [(1, 45), (5, 1)],
        'min_items': 1,
        'max_items': 2,
        'power': 0.5,
        'zone': 1,
        'special_text': "**Special powers:**\n- increased chance to find dirt in `mine`"},

    2: {'name': "Clay Pickaxe",
        'emoji': "<:clay_pickaxe:1014827295669751848>",
        'station': 1,
        'recipe': [(2, 70), (5, 15)],
        'min_items': 1,
        'max_items': 3,
        'power': 1,
        'zone': 1,
        'special_text': "**Special:**\n- increased chance to find clay in `mine`"},

    3: {'name': "Wooden Pickaxe",
        'emoji': "<:wood_pickaxe:1014428473286205441>",
        'station': 1,
        'recipe': [(3, 50), (5, 20), (8, 1)],
        'min_items': 1,
        'max_items': 3,
        'power': 1.5,
        'zone': 1,
        'special_text': "**Special:**\n- increased chance to find logs in `mine`"},

    4: {'name': "Pumpkin Pickaxe",
        'emoji': "<:pumpkin_pick:1014875640220098601>",
        'station': 1,
        'recipe': [(4, 13), (3, 50), (2, 50), (8, 3)],
        'min_items': 1,
        'max_items': 3,
        'power': 2,
        'zone': 1,
        'special_text': "**Special:**\n+15% XP in mine in `zone I`\n"
                        "+1 min item in mine in `zone I`, for total of 2-3 items found."},

    5: {'name': "Sand Pickaxe",
        'emoji': "<:sand_pickaxe:1027504297853853757>",
        'station': 3,
        'recipe': [(16, 30), (3, 10)],
        'min_items': 1,
        'max_items': 2,
        'power': 2.5,
        'zone': 2,
        'special_text': "**Special:**\n- increased chance to find sand in `mine`"},

    6: {'name': "Cactus Pickaxe",
        'emoji': "<:cactus_pickaxe:1027508474843779173>",
        'station': 3,
        'recipe': [(20, 100), (5, 50)],
        'min_items': 1,
        'max_items': 3,
        'power': 3,
        'zone': 2,
        'special_text': "**Special:**\n- increased chance to find cactus in `mine`"},

    7: {'name': "Glass Pickaxe",
        'emoji': "<:glass_pickaxe:1027511893058932748>",
        'station': 3,
        'recipe': [(15, 50), (5, 35), (20, 80)],
        'min_items': 2,
        'max_items': 3,
        'power': 3,
        'zone': 2},

    8: {'name': "Bone Pickaxe",
        'emoji': "<:bone_pickaxe:1027514380256030730>",
        'station': 3,
        'recipe': [(21, 170), (17, 50), (20, 120)],
        'min_items': 1,
        'max_items': 3,
        'power': 3.5,
        'zone': 2,
        'special_text': "**Special:**\n- increased chance to find bones in `mine`"},

    9: {'name': "Copper Pickaxe",
        'emoji': "<:copper_pickaxe:1013755450132549694>",
        'station': 4,
        'recipe': [(18, 10), (22, 5), (21, 150)],
        'min_items': 1,
        'max_items': 3,
        'power': 4,
        'zone': 2,
        'special_text': "**Special:**\n- increased chance to find rare items in `mine`"},
}

""" Recipe [ (item_id, item_amount) ]"""
HOUSES = {
    0: {'name': 'No house ',
        'emoji': '',
        'spaces': 0,
        'description': "You don't own any house yet, try building one with `val build`!"},

    1: {'name': "Dirt Hut",
        'recipe': [(1, 20), (5, 4)],
        'emoji': '<:dirt_hut:1014536882660577331>',
        'spaces': 2,
        'unlocks': 'you can now make `zone I` crafting stations',
        'description': "a simple dirt hut, 4 sticks fixed into the ground and a dirt roof!"},

    2: {'name': "Cactus Hut",
        'recipe': [(20, 100), (16, 100), (6, 25), (21, 25)],
        'emoji': '<:cactus_hut:1027522847486255125>',
        'unlocks': 'you can now keep 3 crafting stations at once',
        'spaces': 3,
        'description': "just don't lean against the walls!"},

}

CRAFTING_STATIONS = {
    1: {'name': "Clay Crafting Slab",
        'recipe': [(2, 10), (5, 1)],
        'unlocks': 'you can now craft the `zone I` gear',
        'emoji': '<:clay_crafting_table:1014538879572914288>',
        'description': "used for crafting `Zone I` gear"},

    2: {'name': "Clay Furnace",
        'recipe': [(2, 30), (3, 20)],
        'unlocks': 'you can now craft bricks!',
        'emoji': '<:clay_furnace:1014871310557515946>',
        'furnace': True,
        'description': "a small furnace for smelting items"},

    3: {'name': "Sandy Bench",
        'recipe': [(16, 15), (2, 50)],
        'unlocks': 'you can now craft the `zone II` gear',
        'emoji': '<:sandy_bench:1027516516440219718>',
        'description': "used for crafting low tier `Zone II` gear"},

    4: {'name': "Copper Anvil",
        'recipe': [(18, 10)],
        'unlocks': 'you can now craft the `zone II` gear',
        'emoji': '<:copper_anvil:1027518843037417523>',
        'description': "used for crafting high tier `Zone II` gear"},

    5: {'name': "Glass Furnace",
        'recipe': [(15, 60), (6, 40)],
        'unlocks': 'you can now craft copper bars!',
        'emoji': '<:glass_furnace:1027520010979131450>',
        'furnace': True,
        'description': "can smelt copper bars"},

}

WEAPONS = {
    0: {'name': "No weapon", 'type': 'normal', 'at': 0, 'str': 0, 'station': 1, 'emoji': '', 'zone': 1,
        'moves': (1,)},

    1: {'name': "Wood stick", 'emoji': '<:tree_branch:1014428457918267453>',
        'recipe': [(5, 1)], 'type': 'normal', 'at': 5, 'str': 0, 'station': 1, 'zone': 1,
        'moves': (1,)},

    2: {'name': "Wood Spear", 'emoji': '<:wood_spear:1019196037702893618>',
        'recipe': [(5, 5), (1, 25)], 'type': 'normal', 'at': 8, 'str': 2, 'station': 1, 'zone': 1,
        'moves': (1,)},

    3: {'name': "Dirt Knife", 'emoji': '<:dirt_knife:1019178237030563870>',
        'recipe': [(5, 2), (1, 40)], 'type': 'light', 'at': 8, 'str': 3, 'station': 1, 'zone': 1,
        'moves': (1,)},

    4: {'name': "Clay Club", 'emoji': '<:clay_club2:1019225691163742209>',
        'recipe': [(2, 40), (1, 40)], 'type': 'normal', 'at': 15, 'str': 5, 'station': 1, 'zone': 1,
        'moves': (1,)},

    5: {'name': "Stick Sai", 'emoji': '<:stick_sai:1019206796621135933>',
        'recipe': [(3, 30), (10, 1)], 'type': 'light', 'at': 14, 'str': 4, 'station': 1, 'zone': 1,
        'moves': (1,)},

    6: {'name': "Wooden Axe", 'emoji': '<:wood_axe:1014428487794315285>',
        'recipe': [(3, 25), (5, 25)], 'type': 'normal', 'at': 25, 'str': 10, 'station': 1, 'zone': 1,
        'moves': (1,)},

    7: {'name': "Wand of Fire", 'emoji': '<:spooky_wand:1019198640398548992>',
        'recipe': [(9, 3), (8, 5), (5, 30)], 'type': 'magic', 'at': 24, 'str': 1, 'station': 1, 'zone': 1,
        'moves': (1, 2)},

    8: {'name': "Rat Axe", 'emoji': '<:rat_axe:1019205318665834496>',
        'recipe': [(7, 5), (3, 30), (9, 1)], 'type': 'normal', 'at': 34, 'str': 15, 'station': 1, 'zone': 1,
        'moves': (1,)},

    9: {'name': "Clay Shield", 'emoji': '<:clay_shield:1019523856161050634>',
        'recipe': [(2, 300), (10, 3), (5, 70)], 'type': 'shield', 'at': 5, 'str': 10, 'station': 1, 'zone': 1,
        'moves': (1, 3)},

    10: {'name': "Fruit Nunchaku", 'emoji': '<:2_fruits:1019189692287164476>',
         'recipe': [(12, 250), (2, 100), (8, 2)], 'type': 'light', 'at': 22, 'str': 7, 'station': 1, 'zone': 1,
         'moves': (1,)},

    11: {'name': "Bricksarigama", 'emoji': '<:bricksagarugama:1019209244521791549>',
         'recipe': [(5, 200), (6, 50), (2, 30)], 'type': 'normal', 'at': 46, 'str': 25, 'station': 1, 'zone': 1,
         'moves': (1,)},

    # ZONE 2 =================================================================================================

    12: {'name': "Glass Spike", 'emoji': '<:glass_spike:1029806123173294150>',
         'recipe': [(15, 20), (16, 20)], 'type': 'light', 'at': 42, 'str': 13, 'station': 3, 'zone': 2,
         'moves': (1,)},

    13: {'name': "Glass Rod", 'emoji': '<:glass_rod:1029806150545322085>',
         'recipe': [(15, 25), (16, 25)], 'type': 'normal', 'at': 86, 'str': 25, 'station': 3, 'zone': 2,
         'moves': (1,)},

    14: {'name': "Bone Shiv", 'emoji': '<:bone_shiv:1030055453566181416>',
         'recipe': [(21, 35), (17, 20)], 'type': 'light', 'at': 82, 'str': 14, 'station': 3, 'zone': 2,
         'moves': (1,)},

    15: {'name': "Sand Scimitar", 'emoji': '<:sand_scimtar:1030062339984195677>',
         'recipe': [(16, 190), (21, 45)], 'type': 'normal', 'at': 142, 'str': 30, 'station': 3, 'zone': 2,
         'moves': (1,)},

    16: {'name': "Copper Knife", 'emoji': '<:copper_knife:1030062391788064778>',
         'recipe': [(18, 4), (22, 7)], 'type': 'light', 'at': 120, 'str': 15, 'station': 4, 'zone': 2,
         'moves': (1,)},

    17: {'name': "Copper Sword", 'emoji': '<:copper_sword:1030062418514161685>',
         'recipe': [(18, 5), (22, 9)], 'type': 'normal', 'at': 210, 'str': 40, 'station': 4, 'zone': 2,
         'moves': (1,)},

    18: {'name': "Wand of Healing", 'emoji': '<:heal_wand:1031156304154202123>',
         'recipe': [(18, 3), (22, 25)], 'type': 'magic', 'at': 98, 'str': 12, 'station': 4, 'zone': 2,
         'moves': (1,)},
}

WEAPON_MOVES = {
    1: {'name': "Attack", 'description': "Type: **BASIC**\nHits for **90-100% of the user's damage**", 'emoji': None},
    2: {'name': "Blaze", 'description': f"""Type: **MAGIC**\nUses **5 {EMOJIS['mana']} mana**. Sets the opponent on fire for INT/5 (rounded up) turns, dealing damage \
equivalent to INT plus the player's damage each turn).\n""", 'emoji': '🔥', 'mana': 5},
    3: {'name': "Defend", 'description': f"""Type: **SUPPORT**\nApplies half of your defense to all party members except you for the next turn, lowering the damage taken.
Example: if you have 100 defense, all party members get +50 defense the next turn""", 'emoji': '🛡'},
}

HELMETS = {
    0: {'name': "No helmet", 'emoji': '', 'def': 0, 'str': 0, 'type': 'normal', 'zone': 1},
    1: {'name': "Dirt Hood", 'recipe': [(1, 30), (2, 5)], 'emoji': '<:dirt_hood:1016660490795094056>',
        'def': 4, 'zone': 1, 'station': 1, 'str': 1, 'type': 'light'},

    2: {'name': "Clay Bowl", 'recipe': [(2, 60), (1, 5)], 'emoji': '<:clay_bowl:1016662872564174878>',
        'def': 6, 'zone': 1, 'station': 1, 'str': 5, 'type': 'normal'},

    3: {'name': "Wooden Helmet", 'recipe': [(3, 30), (5, 40), (2, 3)], 'emoji': '<:wood_helmet:1016765279201677313>',
        'def': 12, 'zone': 1, 'station': 1, 'str': 10, 'type': 'normal'},

    4: {'name': "Leather Hood", 'recipe': [(10, 5), (8, 2)], 'emoji': '<:leader_helm:1016766365518004275>',
        'def': 19, 'zone': 1, 'station': 1, 'str': 20, 'type': 'normal'},

    5: {'name': "Brick Helmet", 'recipe': [(6, 150)], 'emoji': '<:brick_helmet:1017008324316766208>',
        'def': 40, 'zone': 1, 'station': 1, 'str': 25, 'type': 'heavy'},

    6: {'name': "Slimy Hat", 'recipe': [(8, 4), (10, 1)], 'emoji': '<:slimy_hat:1024284903245881374>',
        'def': 11, 'zone': 1, 'station': 1, 'str': 10, 'type': 'light'},

    # ZONE 2 ===============================================

    7: {'name': "Sand Hat", 'recipe': [(16, 60), (20, 15)], 'emoji': '<:sand_hat:1029435409702334534>',
        'def': 20, 'zone': 2, 'station': 3, 'str': 12, 'type': 'light'},

    8: {'name': "Copper Coif", 'recipe': [(18, 4), (21, 70)], 'emoji': '<:copper_coif:1029440723940024382>',
        'def': 37, 'zone': 2, 'station': 4, 'str': 15, 'type': 'light'},

    9: {'name': "Cactus Helmet", 'recipe': [(20, 60), (15, 17)], 'emoji': '<:cactus_helmet:1029807432681132085>',
        'def': 35, 'zone': 2, 'station': 3, 'str': 30, 'type': 'normal'},

    10: {'name': "Carapace Helmet", 'recipe': [(23, 6), (18, 3)], 'emoji': '<:carapace_helmet:1029460462259142656>',
         'def': 45, 'zone': 2, 'station': 4, 'str': 40, 'type': 'normal'},

    11: {'name': "Necro Helmet", 'recipe': [(22, 20), (21, 120)], 'emoji': '<:necro_helmet:1029806210188333058>',
         'def': 30, 'zone': 2, 'station': 4, 'str': 13, 'type': 'normal'},

}

ARMORS = {
    # ZONE 1 ================================================

    0: {'name': "No armor", 'emoji': '', 'def': 0, 'str': 0, 'type': 'normal'},
    1: {'name': "Dirt Rags", 'recipe': [(1, 40), (2, 6)], 'emoji': '<:dirt_rags:1016661493770637432>',
        'def': 7, 'zone': 1, 'station': 1, 'str': 2, 'type': 'light'},

    2: {'name': "Clay Armor", 'recipe': [(2, 80), (1, 6)], 'emoji': '<:clay_armor:1016663696459710504>',
        'def': 15, 'zone': 1, 'station': 1, 'str': 5, 'type': 'normal'},

    3: {'name': "Wooden Chestplate", 'recipe': [(3, 40), (5, 60), (2, 6)], 'emoji': '<:emoji_5:1014428507574640761>',
        'def': 21, 'zone': 1, 'station': 1, 'str': 10, 'type': 'normal'},

    4: {'name': "Leather Armor", 'recipe': [(10, 8), (8, 1)], 'emoji': '<:leather_armor:1016765876579610805>',
        'def': 32, 'zone': 1, 'station': 1, 'str': 20, 'type': 'normal'},

    5: {'name': "Brick Armor", 'recipe': [(6, 200)], 'emoji': '<:brick_armor:1017003519213056040>',
        'def': 60, 'zone': 1, 'station': 1, 'str': 25, 'type': 'heavy'},

    6: {'name': "Slimy Vest", 'recipe': [(8, 8), (10, 2)], 'emoji': '<:slimy_vest:1024284844089417788>',
        'def': 20, 'zone': 1, 'station': 1, 'str': 10, 'type': 'light'},

    # ZONE 2 ================================================

    7: {'name': "Sand Vest", 'recipe': [(16, 80), (20, 20)], 'emoji': '<:sand_vest:1029438264182059008>',
        'def': 35, 'zone': 2, 'station': 3, 'str': 12, 'type': 'light'},

    8: {'name': "Copper Chainmail", 'recipe': [(18, 6), (21, 80)], 'emoji': '<:copper_chainmail:1029441234198085763>',
        'def': 53, 'zone': 2, 'station': 4, 'str': 15, 'type': 'light'},

    9: {'name': "Cactus Armor", 'recipe': [(20, 90), (15, 20)], 'emoji': '<:cactus_armor:1030035717654577202>',
        'def': 42, 'zone': 2, 'station': 3, 'str': 30, 'type': 'normal'},

    10: {'name': "Carapace Armor", 'recipe': [(23, 8), (18, 4)], 'emoji': '<:carapace_armor:1029455575198744587>',
         'def': 55, 'zone': 2, 'station': 4, 'str': 40, 'type': 'normal'},

    11: {'name': "Necro Armor", 'recipe': [(22, 28), (21, 210)], 'emoji': '<:necro_armor:1029806231264702574>',
         'def': 40, 'zone': 2, 'station': 4, 'str': 13, 'type': 'normal'},
}

ENEMIES = {
    0: {'name': 'None', 'emoji': '', 'zone': 1},

    # ZONE 1 ========================================================================================================
    1: {'name': 'Deer', 'emoji': '<:deer:1023927293862760499>', 'dmg': 250, 'dodgeAGI': 800, 'zone': 1, 'drop': 11},
    2: {'name': 'Living Tree', 'emoji': '<:emoji_23:1014991551602098207>', 'dmg': 160, 'dodgeAGI': 300, 'zone': 1,
        'drop': 9},
    3: {'name': 'Wolf', 'emoji': '<:wolf:1015094978873151488>', 'dmg': 80, 'dodgeAGI': 80, 'zone': 1, 'drop': 7},
    4: {'name': 'Snake', 'emoji': '<:snake:1014671124338065449>', 'dmg': 95, 'dodgeAGI': 95, 'zone': 1},
    5: {'name': 'Slime', 'emoji': '<:slime:1016598376533471282>', 'dmg': 60, 'dodgeAGI': 65, 'zone': 1, 'drop': 8},

    # ZONE 2 ========================================================================================================
    6: {'name': 'Tumbleweed', 'emoji': '<:tumbleweed:1027177593201500180>',
        'min_dmg': 200, 'max_dmg': 230, 'dodgeAGI': 115, 'zone': 2},

    7: {'name': 'Desert Crawler', 'emoji': '<:sand_crawler:1027250204862320710>',
        'min_dmg': 240, 'max_dmg': 300, 'dodgeAGI': 130, 'zone': 2, 'drop': 23},

    8: {'name': 'Skeleton', 'emoji': '<:skeleton1:1027251669177745418>',
        'min_dmg': 240, 'max_dmg': 250, 'dodgeAGI': 100, 'zone': 2, 'drop': 21},

    9: {'name': 'Mirrage', 'emoji': '<:miragge:1027253628597178378>',
        'min_dmg': 320, 'max_dmg': 400, 'dodgeAGI': 230, 'zone': 2},

}

BATTLE_ENEMIES = {
    # ZONE 1 ========================================================================================================
    1: {'name': 'Evil Mushroom', 'emoji': '<:evil_mushroom:1021829729315213342>',
        'at_min': 25, 'at_max': 30,
        'hp_min': 1000, 'hp_max': 1200,
        'at+': 5, 'hp+': 55, 'zone': 1},

    2: {'name': 'Beast', 'emoji': '<:forest_beast:1021834967203975239>',
        'at_min': 20, 'at_max': 35,
        'hp_min': 600, 'hp_max': 700,
        'at+': 6, 'hp+': 30, 'zone': 1},

    3: {'name': 'Gelatinous Abomination', 'emoji': '<:gelatinous_abomination:1021832192814493836>',
        'at_min': 15, 'at_max': 20,
        'hp_min': 500, 'hp_max': 600,
        'at+': 5, 'hp+': 130, 'zone': 1},

    4: {'name': 'Giant Bunny', 'emoji': '<:giant_bunny:1022024794251722803>',
        'at_min': 20, 'at_max': 25,
        'hp_min': 700, 'hp_max': 900,
        'at+': 5, 'hp+': 55, 'zone': 1},

    5: {'name': 'Basilisk', 'emoji': '<:basilisk:1021839651046174764>',
        'at_min': 15, 'at_max': 20,
        'hp_min': 300, 'hp_max': 500,
        'at+': 8, 'hp+': 50, 'zone': 1},

    6: {'name': "MUD GOLEM SPAWNER", 'emoji': '<:mud_golem_spawner:1026094289723334747>'},

    # ZONE 2 ========================================================================================================

    7: {'name': 'Sand Devil', 'emoji': '<:sand_devil:1029390526904021052>',
        'at_min': 80, 'at_max': 95,
        'hp_min': 1300, 'hp_max': 1400,
        'at+': 5, 'hp+': 50, 'zone': 2},

    8: {'name': 'Sandmadillo', 'emoji': '<:sandmadillo:1029390554154418186>',
        'at_min': 75, 'at_max': 80,
        'hp_min': 1000, 'hp_max': 1200,
        'at+': 8, 'hp+': 60, 'zone': 2},

    9: {'name': 'Cactratotes', 'emoji': '<:cactottes:1029390483430047764>',
        'at_min': 80, 'at_max': 95,
        'hp_min': 1200, 'hp_max': 1800,
        'at+': 5, 'hp+': 75, 'zone': 2},

    10: {'name': 'Mummy', 'emoji': '<:mummy:1029390459455426580>',
         'at_min': 75, 'at_max': 80,
         'hp_min': 1000, 'hp_max': 1200,
         'at+': 5, 'hp+': 70, 'zone': 2},
}


def get_pickaxe_recipes(pickaxe_list):
    text = ""
    for pick in pickaxe_list:
        text += f"""**__{PICKAXES[pick]['emoji']} {PICKAXES[pick]['name']}__**: {get_recipe_text(PICKAXES[pick]['recipe'])}
**Power:** {PICKAXES[pick]['power']} — **Items found:** {PICKAXES[pick]['min_items']}-{PICKAXES[pick]['max_items']}"""
        # if 'special_text' in PICKAXES[pick]:
        #     text += f"\n{PICKAXES[pick]['special_text']}"

        text += '\n\n'

    return text


def get_weapon_recipes(weapon_list):
    texts = []
    for weapon in weapon_list:
        texts += [
            f"""{WEAPONS[weapon]['emoji']} __**{WEAPONS[weapon]['name']}**:__ {get_recipe_text(WEAPONS[weapon]['recipe'])}
**STR: {WEAPONS[weapon]['str']}** - **Type: {WEAPONS[weapon]['type']}** - {WEAPONS[weapon]['at']}{EMOJIS['at']}"""]

    return '\n\n'.join(texts)


def get_armor_recipes(armor_lst):
    texts = []
    for armor, _type in armor_lst:
        if _type == 1:
            texts += [
                f"""{HELMETS[armor]['emoji']} __**{HELMETS[armor]['name']}**:__ {get_recipe_text(HELMETS[armor]['recipe'])}
**STR: {HELMETS[armor]['str']}** - **Type: {HELMETS[armor]['type']}** - {HELMETS[armor]['def']}{EMOJIS['def']}"""]

        else:
            texts += [
                f"""{ARMORS[armor]['emoji']} __**{ARMORS[armor]['name']}**:__ {get_recipe_text(ARMORS[armor]['recipe'])}
**STR: {ARMORS[armor]['str']}** - **Type: {ARMORS[armor]['type']}**  - {ARMORS[armor]['def']}{EMOJIS['def']}"""]

    return '\n\n'.join(texts)


RECIPES = {
    1: {'pickaxe': f"""
**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']} required!**

{get_pickaxe_recipes([1, 2, 3, 4])}""",

        'weapon': {1: F"""
**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']} required!**   

{get_weapon_recipes([1, 2, 3, 4, 5, 6])}""",
                   2: F"""**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']} required!**   

{get_weapon_recipes([7, 8, 9, 10, 11])}"""},

        'item': f"""
**{CRAFTING_STATIONS[2]['emoji']} {CRAFTING_STATIONS[2]['name']} required!**

**__{ITEMS[6]['emoji']} {ITEMS[6]['name']}__**: {get_recipe_text(ITEMS[6]['recipe'])}
🕑 `Smelt time:` {get_pretty_time(ITEMS[6]['smelt_time'])}

**__{ITEMS[10]['emoji']} {ITEMS[10]['name']}__**: {get_recipe_text(ITEMS[10]['recipe'])}
🕑 `Smelt time:` {get_pretty_time(ITEMS[10]['smelt_time'])}

**__{ITEMS[13]['emoji']} {ITEMS[13]['name']}__**: {get_recipe_text(ITEMS[13]['recipe'])}
🕑 `Smelt time:` {get_pretty_time(ITEMS[13]['smelt_time'])} — **Heal power:** 150HP
**Special:** Heals HP to max while in zone I & II.""",

        'armor': {1: f"""
**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']} required!**

{get_armor_recipes([(1, 1), (1, 0),
                    (2, 1), (2, 0),
                    (3, 1), (3, 0)])}""",
                  2: f"""
**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']} required!**

{get_armor_recipes([(6, 1), (6, 0),
                    (4, 1), (4, 0),
                    (5, 1), (5, 0)])}"""},

        'build': f"""
__**{HOUSES[1]['emoji']} {HOUSES[1]['name']}:**__ {get_recipe_text(HOUSES[1]['recipe'])}
Required for placing crafting stations! — **Space:** 2

__**{CRAFTING_STATIONS[1]['emoji']} {CRAFTING_STATIONS[1]['name']}**:__ {get_recipe_text(CRAFTING_STATIONS[1]['recipe'])}
- {CRAFTING_STATIONS[1]['description']}

__**{CRAFTING_STATIONS[2]['emoji']} {CRAFTING_STATIONS[2]['name']}**:__ {get_recipe_text(CRAFTING_STATIONS[2]['recipe'])}
- {CRAFTING_STATIONS[2]['description']}"""},

    # =============================================================================

    2: {'pickaxe': f"""
**{CRAFTING_STATIONS[3]['emoji']} {CRAFTING_STATIONS[3]['name']} required!**

{get_pickaxe_recipes([5, 6, 7, 8, 9])}""",

        'build': f"""
__**{HOUSES[2]['emoji']} {HOUSES[2]['name']}:**__ {get_recipe_text(HOUSES[2]['recipe'])}
Required for placing crafting stations! — **Space:** 3

__**{CRAFTING_STATIONS[3]['emoji']} {CRAFTING_STATIONS[3]['name']}**:__ {get_recipe_text(CRAFTING_STATIONS[3]['recipe'])}
- {CRAFTING_STATIONS[3]['description']}

__**{CRAFTING_STATIONS[4]['emoji']} {CRAFTING_STATIONS[4]['name']}**:__ {get_recipe_text(CRAFTING_STATIONS[4]['recipe'])}
- {CRAFTING_STATIONS[4]['description']}

__**{CRAFTING_STATIONS[5]['emoji']} {CRAFTING_STATIONS[5]['name']}**:__ {get_recipe_text(CRAFTING_STATIONS[5]['recipe'])}
- {CRAFTING_STATIONS[5]['description']}""",

        'item': f"""
**{CRAFTING_STATIONS[2]['emoji']} {CRAFTING_STATIONS[2]['name']} required!**
**__{ITEMS[15]['emoji']} {ITEMS[15]['name']}__**: {get_recipe_text(ITEMS[15]['recipe'])}
🕑 `Smelt time:` {get_pretty_time(ITEMS[15]['smelt_time'])}

**{CRAFTING_STATIONS[5]['emoji']} {CRAFTING_STATIONS[5]['name']} required!**
**__{ITEMS[18]['emoji']} {ITEMS[18]['name']}__**: {get_recipe_text(ITEMS[18]['recipe'])}
🕑 `Smelt time:` {get_pretty_time(ITEMS[18]['smelt_time'])}""",

        'armor': {1: f"""\
**{CRAFTING_STATIONS[3]['emoji']} {CRAFTING_STATIONS[3]['name']} required!**

{get_armor_recipes([(7, 1), (7, 0),
                    (9, 1), (9, 0)])}""",

                  2: f"""\
**{CRAFTING_STATIONS[4]['emoji']} {CRAFTING_STATIONS[4]['name']} required!**

{get_armor_recipes([(8, 1), (8, 0),
                    (10, 1), (10, 0),
                    (11, 1), (11, 0)])}"""},

        'weapon': {1: F"""
**{CRAFTING_STATIONS[3]['emoji']} {CRAFTING_STATIONS[3]['name']} required!**   

{get_weapon_recipes([12, 13, 14, 15])}""",
                   2: F"""
**{CRAFTING_STATIONS[4]['emoji']} {CRAFTING_STATIONS[4]['name']} required!**   

{get_weapon_recipes([16, 17, 18])}"""}, }
}

HUNT_PHASES_search = ['seeking enemies in', 'hunting enemies in', 'tracking enemies in', 'looking for enemies in',
                      'stalking enemies in', 'rummaging for enemies in', 'searching for enemies in']

HUNT_PHASES_found = ['found', 'encountered', 'met']
HUNT_PHASES_kill = ['killed', 'slain', 'butchered', 'crushed', 'defeated',
                    'wiped out', 'annihilated', 'eliminated', 'slaughtered']

SORT_ORDER = {1:
                  [1, 2, 5, 3, 12, 13, 4, 6, 7, 8, 9, 10, 11],
              2: [16, 20, 21, 15, 17, 19, 18, 22]}


def get_it_from_name(name: str) -> typing.Tuple[int, str]:
    """
    Returns the (ID, category) for the name given
    """

    for pickaxe in PICKAXES:
        if PICKAXES[pickaxe]['name'].lower() == name:
            return pickaxe, 'pickaxe'

    for item in ITEMS:
        if ITEMS[item]['name'].lower() == name:
            return item, 'item'

    for crate in CRATES:
        if CRATES[crate]['name'].lower() == name:
            return crate, 'crate'

    for station in CRAFTING_STATIONS:
        if CRAFTING_STATIONS[station]['name'].lower() == name:
            return station, 'station'

    for helm in HELMETS:
        if HELMETS[helm]['name'].lower() == name:
            return helm, 'helmet'

    for weap in WEAPONS:
        if WEAPONS[weap]['name'].lower() == name:
            return weap, 'weapon'

    for armor in ARMORS:
        if ARMORS[armor]['name'].lower() == name:
            return armor, 'armor'

    for house in HOUSES:
        if HOUSES[house]['name'].lower() == name:
            return house, 'house'

    for enemy in ENEMIES:
        if ENEMIES[enemy]['name'].lower() == name:
            return enemy, 'enemy'

    for enemy in BATTLE_ENEMIES:
        if BATTLE_ENEMIES[enemy]['name'].lower() == name:
            return enemy, 'battle_enemy'

    return 0, ''


def general_pickaxe_info_text(pickaxe_id, equiped):
    return f"""**{PICKAXES[pickaxe_id]['emoji']} {PICKAXES[pickaxe_id]['name']}** {'**[EQUIPPED]**' if equiped else ''}
    
**Zone {int_to_roman(PICKAXES[pickaxe_id]['zone'])} pickaxe**
**Power:** {PICKAXES[pickaxe_id]['power']}
**Items Found:** {PICKAXES[pickaxe_id]['min_items']}-{PICKAXES[pickaxe_id]['max_items']}
**Crafting Station:** {CRAFTING_STATIONS[PICKAXES[pickaxe_id]['station']]['emoji']} {CRAFTING_STATIONS[PICKAXES[pickaxe_id]['station']]['name']}
**Recipe:** {get_recipe_text(PICKAXES[pickaxe_id]['recipe'])}

{f"{PICKAXES[pickaxe_id]['special_text'] if 'special_text' in PICKAXES[pickaxe_id] else ''}"}
"""


def general_weapon_info_text(weapon, equiped):
    text = f"""**{WEAPONS[weapon]['emoji']} {WEAPONS[weapon]['name']}** {'**[EQUIPPED]**' if equiped else ''}
    
**Zone {int_to_roman(WEAPONS[weapon]['zone'])} weapon**
**Base damage:** {WEAPONS[weapon]['at']} {EMOJIS['at']}
**Type:** {WEAPONS[weapon]['type'].title()}
**Crafting Station:** {CRAFTING_STATIONS[WEAPONS[weapon]['station']]['emoji']} {CRAFTING_STATIONS[WEAPONS[weapon]['station']]['name']}
**Recipe:** {get_recipe_text(WEAPONS[weapon]['recipe'])}
{f"{WEAPONS[weapon]['special_text'] if 'special_text' in WEAPONS[weapon] else ''}"}
> **————— ABILITIES —————**
"""
    for move in WEAPONS[weapon]['moves']:
        text += f"""**{WEAPON_MOVES[move]['emoji']} {WEAPON_MOVES[move]['name']}:**
{WEAPON_MOVES[move]['description']}

"""
    return text


def general_helmet_info_text(helmet_id, equipped):
    return f"""**{HELMETS[helmet_id]['emoji']} {HELMETS[helmet_id]['name']}** {'**[EQUIPPED]**' if equipped else ''}
    
**Zone {int_to_roman(HELMETS[helmet_id]['zone'])} helmet**
**Base defense** {HELMETS[helmet_id]['def']} {EMOJIS['def']}
**Type:** {HELMETS[helmet_id]['type']}
**Crafting Station:** {CRAFTING_STATIONS[HELMETS[helmet_id]['station']]['emoji']} {CRAFTING_STATIONS[HELMETS[helmet_id]['station']]['name']}
**Recipe:** {get_recipe_text(HELMETS[helmet_id]['recipe'])}

{f"{HELMETS[helmet_id]['special_text'] if 'special_text' in HELMETS[helmet_id] else ''}"}
"""


def general_armor_info_text(armor_id, equipped):
    return f"""**{ARMORS[armor_id]['emoji']} {ARMORS[armor_id]['name']}** {'**[EQUIPPED]**' if equipped else ''}
    
**Zone {int_to_roman(ARMORS[armor_id]['zone'])} armor**
**Base defense** {ARMORS[armor_id]['def']} {EMOJIS['def']}
**Type:** {ARMORS[armor_id]['type']}
**Crafting Station:** {CRAFTING_STATIONS[ARMORS[armor_id]['station']]['emoji']} {CRAFTING_STATIONS[ARMORS[armor_id]['station']]['name']}
**Recipe:** {get_recipe_text(ARMORS[armor_id]['recipe'])}

{f"{ARMORS[armor_id]['special_text'] if 'special_text' in ARMORS[armor_id] else ''}"}
"""


def general_enemy_info_text(enemy):
    text = f"""**{ENEMIES[enemy]['emoji']} {ENEMIES[enemy]['name']}**

Can be found in `seek` in `zone {int_to_roman(ENEMIES[enemy]['zone'])}`.
"""
    if 'drop' in ENEMIES[enemy]:
        drop_id = ENEMIES[enemy]['drop']
        text += f"Drops **{ITEMS[drop_id]['emoji']} {ITEMS[drop_id]['name']}**\n"
    else:
        text += "Does not drop anything.\b"

    return text


def general_battle_enemy_info_text(enemy):
    text = f"""**{BATTLE_ENEMIES[enemy]['emoji']} {BATTLE_ENEMIES[enemy]['name']}**

Can be found in `battle` in `zone {int_to_roman(BATTLE_ENEMIES[enemy]['zone'])}`.
"""

    return text


def general_item_info_text(item_id):
    text = f"""**{ITEMS[item_id]['emoji']} {ITEMS[item_id]['name']}**
"""

    if 'command' in ITEMS[item_id]:
        text += f"Found in `zone {int_to_roman(ITEMS[item_id]['zone'])}` in `{ITEMS[item_id]['command']}`."

    elif 'smelt_time' in ITEMS[item_id]:
        text += f"""Crafted at a furnace in `zone {int_to_roman(ITEMS[item_id]['zone'])}`.
**Crafting Station:** at least {CRAFTING_STATIONS[ITEMS[item_id]['station']]['emoji']} {CRAFTING_STATIONS[ITEMS[item_id]['station']]['name']}
**Recipe:** {get_recipe_text(ITEMS[item_id]['recipe'])}
**Time to smelt: {get_pretty_time(ITEMS[item_id]['smelt_time'])}**
"""
    if 'fuel_power' in ITEMS[item_id]:
        text += f"\n**Burns for: {get_pretty_time(ITEMS[item_id]['fuel_power'])}** when used as fuel"

    if 'heal_power' in ITEMS[item_id]:
        text += f"\nHeals the user for **{ITEMS[item_id]['heal_power']} HP** when consumed."

    if 'effect' in ITEMS[item_id]:
        text += f"\n{ITEMS[item_id]['effect']}"

    return text


def get_hp_bar(hp: int, max_hp: int) -> str:
    percent_lost = math.ceil(hp / max_hp / 0.1)

    hp_bar = ''
    if percent_lost > 3:
        for i in range(10):
            if i == 0 and percent_lost:
                hp_bar += EMOJIS['gbl']
            elif i == 0:
                hp_bar += EMOJIS['ebl']

            elif i == 9 and percent_lost == 10:
                hp_bar += EMOJIS['gbr']
            elif i == 9 and percent_lost < 10:
                hp_bar += EMOJIS['ebr']

            elif percent_lost > i:
                hp_bar += EMOJIS['gbm']
            elif percent_lost <= i:
                hp_bar += EMOJIS['ebm']

    else:
        for i in range(10):
            if i == 0 and percent_lost:
                hp_bar += EMOJIS['rbl']
            elif i == 0:
                hp_bar += EMOJIS['ebl']

            elif i == 9 and percent_lost == 10:
                hp_bar += EMOJIS['rbr']
            elif i == 9 and percent_lost < 10:
                hp_bar += EMOJIS['ebr']

            elif percent_lost > i:
                hp_bar += EMOJIS['rbm']
            elif percent_lost <= i:
                hp_bar += EMOJIS['ebm']

    return hp_bar


ALL_NAMES = ['traits', 'battle', 'seek']
ALL_CRAFTABLES = []


def make_all_names(container, for_craft=False):
    for pickaxe in PICKAXES:
        if for_craft and 'recipe' not in PICKAXES[pickaxe]:
            continue
        container.append(PICKAXES[pickaxe]['name'].lower())

    for item in ITEMS:
        if for_craft and 'recipe' not in ITEMS[item]:
            continue
        container.append(ITEMS[item]['name'].lower())

    for station in CRAFTING_STATIONS:
        container.append(CRAFTING_STATIONS[station]['name'].lower())

    for helm in HELMETS:
        if for_craft and 'recipe' not in HELMETS[helm]:
            continue
        container.append(HELMETS[helm]['name'].lower())

    for weap in WEAPONS:
        if for_craft and 'recipe' not in WEAPONS[weap]:
            continue
        container.append(WEAPONS[weap]['name'].lower())

    for armor in ARMORS:
        if for_craft and 'recipe' not in ARMORS[armor]:
            continue
        container.append(ARMORS[armor]['name'].lower())

    for house in HOUSES:
        container.append(HOUSES[house]['name'].lower())

    if not for_craft:
        for enemy in ENEMIES:
            container.append(ENEMIES[enemy]['name'].lower())

        for enemy in BATTLE_ENEMIES:
            container.append(BATTLE_ENEMIES[enemy]['name'].lower())


make_all_names(ALL_NAMES)
make_all_names(ALL_CRAFTABLES, for_craft=True)

CRATE_ITEMS_PER_AREA = {}

for i in range(1, len(ZONES) + 1):
    CRATE_ITEMS_PER_AREA[i] = {'common': [], 'uncommon': [], 'rare': [], 'very rare': [], 'epic': [], 'legendary': [],
                               'insane': []}

for item in ITEMS:
    if not item:
        continue

    if ITEMS[item]['rarity'] == 1:
        CRATE_ITEMS_PER_AREA[ITEMS[item]['zone']]['common'].append(item)

    elif ITEMS[item]['rarity'] == 2:
        CRATE_ITEMS_PER_AREA[ITEMS[item]['zone']]['uncommon'].append(item)

    elif ITEMS[item]['rarity'] == 3:
        CRATE_ITEMS_PER_AREA[ITEMS[item]['zone']]['rare'].append(item)

    elif ITEMS[item]['rarity'] == 4:
        CRATE_ITEMS_PER_AREA[ITEMS[item]['zone']]['very rare'].append(item)


def generate_text_all_emojis(items: typing.List):
    text = ""
    for item in items:
        text += f"{ITEMS[item]['emoji']} "

    return text


def get_area_crate_rewards(area):
    text = f"> {random.choice(ZONES[area]['emoji'])} **Zone {int_to_roman(area)} rewards:**\n\n"
    if CRATE_ITEMS_PER_AREA[area]['common']:
        text += f"""🔸 **__Common loot:__** {generate_text_all_emojis(CRATE_ITEMS_PER_AREA[area]['common'])}\n"""

    if CRATE_ITEMS_PER_AREA[area]['uncommon']:
        text += f"""🔸 **__Uncommon loot:__** {generate_text_all_emojis(CRATE_ITEMS_PER_AREA[area]['uncommon'])}\n"""

    if CRATE_ITEMS_PER_AREA[area]['rare']:
        text += f"""🔸 **__Rare loot:__** {generate_text_all_emojis(CRATE_ITEMS_PER_AREA[area]['rare'])}\n"""

    if CRATE_ITEMS_PER_AREA[area]['very rare']:
        text += f"""🔸 **__Very Rare loot:__** {generate_text_all_emojis(CRATE_ITEMS_PER_AREA[area]['very rare'])}\n"""

    return text


COMMANDS = {
    1: {'name': "mine"},
    2: {'name': "seek"},
    3: {'name': "battle"},
    4: {'name': 'help'},
    5: {'name': 'cooldown'},
    6: {'name': 'ready'},
    7: {'name': 'profile'},
    8: {'name': 'inventory'},
    9: {'name': 'build'},
    10: {'name': 'craft'},
    11: {'name': 'destroy'},
    12: {'name': 'crates'},
    13: {'name': 'open'},
    14: {'name': 'use'},
    15: {'name': 'equip'},
    16: {'name': 'add fuel'},
    17: {'name': 'remove fuel'},
    18: {'name': 'heal'},
    19: {'name': 'rebuild'},
    20: {'name': 'progress'},
}


COMMANDS_WITH_COOLDOWN = {1, 2, 3, 20}