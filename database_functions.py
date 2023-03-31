import time
import typing

from global_variables import psql_conn, DATA_CACHE


def initialize_db():
    """Runs all the commands required to create the tables, in case I use it on a new DB"""

    cursor = psql_conn.cursor()
    # Player_stats TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS player_stats 
                  (player_id BIGINT PRIMARY KEY,
                   area INT DEFAULT 1,
                   health bigint DEFAULT 0,
                   max_health bigint DEFAULT 100,
                   trait_points int DEFAULT 0,
                   current_xp bigint DEFAULT 0,
                   level int DEFAULT 1,
                   mana bigint DEFAULT 0,
                   max_mana bigint DEFAULT 0,
                   max_area int DEFAULT 1
);""")
    # Player_gear TABLE ==============================================================================
    cursor.execute("CREATE TABLE IF NOT EXISTS player_gear "
                   "(player_id BIGINT PRIMARY KEY,"
                   " pickaxe int DEFAULT 0,"
                   " weapon int DEFAULT 0,"
                   " helmet int DEFAULT 0,"
                   " chest int DEFAULT 0);")

    # inventory TABLE ==============================================================================
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS inventory (player_id BIGINT, item_id int, item_amount bigint, PRIMARY KEY (player_id, item_id));")

    # Crate inventory TABLE ==============================================================================
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS crates (player_id BIGINT, crate_id int, crate_amount bigint, PRIMARY KEY (player_id, crate_id));")

    # cooldowns TABLE ==============================================================================
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cooldowns (player_id BIGINT, command_id int, last_used float8, PRIMARY KEY (player_id, command_id));")

    # houses TABLE ==============================================================================
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS houses (player_id BIGINT, house_id int, is_owned int, PRIMARY KEY (player_id, house_id));")
    cursor.execute("ALTER TABLE houses ALTER COLUMN is_owned SET DEFAULT 0;")

    # crafting_stations TABLE ==============================================================================
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS crafting_stations (player_id BIGINT, station_id int, slot_in_house int);")

    # furnaces TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS furnaces 
    (player_id bigint,
     furnace_id int DEFAULT 0,
      furnace_slot int DEFAULT 0,
       last_viewed bigint DEFAULT 0, 
       item_id_inside int DEFAULT 0,
       item_amount_inside bigint DEFAULT 0,
       fuel_id_inside int DEFAULT 0,
       fuel_amount_inside bigint DEFAULT 0,
       next_fuel_burn bigint DEFAULT 0,
       next_item_burn bigint DEFAULT 0,
       
       PRIMARY KEY (player_id, furnace_id, furnace_slot));""")
    # Traits TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS player_traits 
        (player_id bigint PRIMARY KEY,
        _str int DEFAULT 0,
        _agi int DEFAULT 0,
        _end int DEFAULT 0,
        _int int DEFAULT 0,
        _luk int DEFAULT 0,
        _per int DEFAULT 0);
""")
    # PICKAXES OWNED TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS owned_pickaxes (
player_id bigint,
pickaxe_id int,
PRIMARY KEY (player_id, pickaxe_id));""")

    # OWNED ARMOR TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS owned_armors (
player_id bigint,
armor_id int,
PRIMARY KEY (player_id, armor_id));""")

    # OWNED HELMETS TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS owned_helmets (
player_id bigint,
helmet_id int,
PRIMARY KEY (player_id, helmet_id));""")

    # OWNED WEAPONS TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS owned_weapons (
player_id bigint,
weapon_id int,
PRIMARY KEY (player_id, weapon_id));""")

    # ZONE REQ TABLE ==============================================================================
    cursor.execute("""CREATE TABLE IF NOT EXISTS zone_completed (
player_id bigint,
zone_id int,
PRIMARY KEY (player_id, zone_id));""")

    cursor.close()
    psql_conn.commit()
    print("Database initialization successful")


def advance_zone(player_id, zone_id):
    cursor = psql_conn.cursor()
    cursor.execute("""UPDATE player_stats SET max_area = %s, area = %s WHERE player_id=%s;""",
                   (zone_id, zone_id, player_id))

    DATA_CACHE[player_id]['zone'] = zone_id

    cursor.close()
    psql_conn.commit()


def get_zone_and_max(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT area, max_area FROM player_stats WHERE player_id=%s;",
                   (player_id,))

    zone = cursor.fetchall()

    return zone[0]


def set_current_zone(player_id, zone_id):
    cursor = psql_conn.cursor()
    cursor.execute("""UPDATE player_stats SET area = %s WHERE player_id=%s;""",
                   (zone_id, player_id))

    DATA_CACHE[player_id]['zone'] = zone_id

    cursor.close()
    psql_conn.commit()


def get_zone_status(player_id, zone_id):
    cursor = psql_conn.cursor()
    cursor.execute("""SELECT zone_id FROM zone_completed WHERE player_id = %s AND zone_id = %s;""",
                   (player_id, zone_id))

    return 1 if cursor.fetchone() else 0


def set_zone_req_complete(player_id, zone_id):
    cursor = psql_conn.cursor()
    cursor.execute("""INSERT INTO zone_completed (player_id, zone_id) VALUES (%s, %s);""", (player_id, zone_id))
    psql_conn.commit()


def get_user_crates(player_id: int) -> dict:
    cursor = psql_conn.cursor()
    cursor.execute("SELECT crate_id, crate_amount FROM crates WHERE player_id=%s;",
                   (player_id,))

    crates = cursor.fetchall()
    crate_dict = {}

    for crate_id, crate_amount in sorted(crates):
        if crate_amount:
            crate_dict[crate_id] = crate_amount

    return crate_dict


def add_crates(player_id: int, crate_id: int, crate_amount: int):
    cursor = psql_conn.cursor()
    cursor.execute("""INSERT INTO crates (player_id, crate_id, crate_amount)
VALUES (%s, %s, %s)
ON CONFLICT (player_id, crate_id) DO
UPDATE SET crate_amount = crates.crate_amount + %s WHERE crates.player_id=%s and crates.crate_id=%s;""",
                   (player_id, crate_id, crate_amount, crate_amount, player_id, crate_id))
    cursor.close()


def remove_crates(player_id: int, crate_id: int, crate_amount: int):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE crates SET crate_amount = crate_amount - %s WHERE player_id=%s AND crate_id=%s;",
                   (crate_amount, player_id, crate_id))
    cursor.close()


def reset_progress(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("DELETE FROM player_stats WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM player_gear WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM houses WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM inventory WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM cooldowns WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM crafting_stations WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM furnaces WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM player_traits WHERE player_id=%s;", (player_id,))

    cursor.execute("DELETE FROM owned_helmets WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM crates WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM owned_pickaxes WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM owned_armors WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM owned_weapons WHERE player_id=%s;", (player_id,))
    cursor.execute("DELETE FROM zone_completed WHERE player_id=%s;", (player_id,))

    if player_id in DATA_CACHE:
        del DATA_CACHE[player_id]
    cursor.close()
    psql_conn.commit()


def level_up(player_id, new_level, overflow):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_stats SET level=%s, current_xp=%s, trait_points=trait_points+5 WHERE player_id=%s;",
                   (new_level, overflow, player_id))

    cursor.close()
    psql_conn.commit()


def level_down_zero(player_id, remove_level_amt):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_stats SET level=level-%s, current_xp=0 WHERE player_id=%s;",
                   (remove_level_amt, player_id))

    cursor.close()
    psql_conn.commit()


def add_xp(player_id, xp):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET current_xp=current_xp+%s WHERE player_id=%s;", (xp, player_id))
    cursor.close()
    psql_conn.commit()


def get_xp(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT current_xp, level FROM player_stats WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()[0]


def add_max_hp(player_id, hp_to_add):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET health=health+%s, max_health=max_health+%s WHERE player_id=%s;",
                   (hp_to_add, hp_to_add, player_id))
    cursor.close()
    psql_conn.commit()


def add_max_mana(player_id, mana_to_add):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET mana=mana+%s, max_mana=max_mana+%s WHERE player_id=%s;",
                   (mana_to_add, mana_to_add, player_id))
    cursor.close()
    psql_conn.commit()


def reset_max_mana(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET mana=0, max_mana=0 WHERE player_id=%s;", (player_id,))
    cursor.close()
    psql_conn.commit()


def set_mana(player_id, mana):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET mana=%s WHERE player_id=%s;",
                   (mana, player_id))
    cursor.close()
    psql_conn.commit()


def update_traits(player_id: int,
                  trait_list: typing.List[int],
                  current_str: int,
                  current_per: int,
                  current_int: int) -> None:
    cursor = psql_conn.cursor()

    _str, _agi, _end, _int, _luk, _per = trait_list

    if _str and ((current_str % 3) + _str) // 3:
        # Add 1 HP for every 3 points
        add_max_hp(player_id, ((current_str % 3) + _str) // 3)

    if _end:
        add_max_hp(player_id, _end * 3)

    if _int + current_int >= 10:
        if current_int >= 10:
            # If it was already 10, add the new mana from INT and PER
            add_max_mana(player_id, _int + (((current_per % 3) + _per) // 3))

        else:
            # If it reached 10 now, also add all the mana from their PER
            add_max_mana(player_id, ((_int + current_int) - 10) + (current_per // 3))

    cursor.execute("UPDATE player_traits SET"
                   " _str=_str+%s,"
                   " _agi=_agi+%s,"
                   " _end=_end+%s,"
                   " _int=_int+%s,"
                   " _luk=_luk+%s,"
                   " _per=_per+%s "
                   "WHERE player_id=%s;", (_str, _agi, _end, _int, _luk, _per, player_id))

    if player_id in DATA_CACHE and 'traits' in DATA_CACHE[player_id]:
        del DATA_CACHE[player_id]['traits']

    cursor.close()
    psql_conn.commit()


def update_remove_traits(player_id: int, trait_list: typing.List[int], current_int, current_per) -> None:
    """
    The trait_list will be negative numbers!
    """
    cursor = psql_conn.cursor()
    _str, _agi, _end, _int, _luk, _per = trait_list

    if _str:
        add_max_hp(player_id, -(abs(_str) // 3))

    if _end:
        add_max_hp(player_id, _end * 3)

    if _int:
        if (current_int - 10) + _int < 0:
            _per = 0

            reset_max_mana(player_id)
        else:
            mana_to_remove = -_int
            add_max_mana(player_id, -mana_to_remove)

    if current_int + _int >= 10 and _per:
        add_max_mana(player_id, -(abs(_per) // 3))

    cursor.execute("UPDATE player_traits SET"
                   " _str=_str+%s,"
                   " _agi=_agi+%s,"
                   " _end=_end+%s,"
                   " _int=_int+%s,"
                   " _luk=_luk+%s,"
                   " _per=_per+%s "
                   "WHERE player_id=%s;", (_str, _agi, _end, _int, _luk, _per, player_id))

    if player_id in DATA_CACHE and 'traits' in DATA_CACHE[player_id]:
        del DATA_CACHE[player_id]['traits']

    cursor.close()
    psql_conn.commit()


def get_traits(player_id):
    if player_id in DATA_CACHE and 'traits' in DATA_CACHE[player_id]:
        return DATA_CACHE[player_id]['traits']

    cursor = psql_conn.cursor()
    cursor.execute("SELECT * FROM player_traits WHERE player_id=%s;", (player_id,))

    stats = cursor.fetchall()
    if not stats:
        cursor.execute("INSERT INTO player_traits (player_id) VALUES (%s);", (player_id,))
        psql_conn.commit()
        return 0, 0, 0, 0, 0, 0

    if player_id in DATA_CACHE:
        DATA_CACHE[player_id]['traits'] = stats[0][1:]

    return stats[0][1:]


def add_trait_points(player_id, amount):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET trait_points=trait_points+%s WHERE player_id=%s;", (amount, player_id))
    cursor.close()
    psql_conn.commit()


def get_left_on_item(player_id, slot):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT next_item_burn FROM furnaces WHERE player_id=%s AND furnace_slot=%s;", (player_id, slot))

    return cursor.fetchall()[0][0]


def set_furnace_view_last(player_id, furnace_slot, next_fuel, next_item):
    cursor = psql_conn.cursor()
    cursor.execute(
        "UPDATE furnaces SET last_viewed=%s, next_fuel_burn=%s, next_item_burn=%s WHERE player_id=%s AND furnace_slot=%s;",
        (int(time.time()), next_fuel, next_item, player_id, furnace_slot))
    cursor.close()
    psql_conn.commit()


def get_current_fuel_in_furnace(player_id, furnace_slot):
    cursor = psql_conn.cursor()
    cursor.execute(
        "SELECT fuel_id_inside, fuel_amount_inside, next_fuel_burn FROM furnaces WHERE player_id=%s AND furnace_slot=%s;",
        (player_id, furnace_slot))

    return cursor.fetchall()[0]


def get_current_item_in_furnace(player_id, furnace_slot):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT (item_id_inside, item_amount_inside) FROM furnaces WHERE player_id=%s AND furnace_slot=%s;",
                   (player_id, furnace_slot))

    item, amount = [int(i) for i in cursor.fetchall()[0][0].replace('(', '').replace(')', '').split(',')]

    return item, amount


def get_all_furnaces(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT furnace_slot, item_id_inside FROM furnaces WHERE player_id=%s;", (player_id,))

    furnaces = cursor.fetchall()

    cursor.close()
    return furnaces


def add_fuel(player_id, item_id, amount, furnace_slot, burn_time=0):
    cursor = psql_conn.cursor()

    remove_item(player_id, item_id, amount)

    if burn_time:
        cursor.execute(
            "UPDATE furnaces SET fuel_id_inside=%s, fuel_amount_inside=fuel_amount_inside+%s, next_fuel_burn=%s, last_viewed=%s WHERE player_id=%s AND furnace_slot=%s;",
            (item_id, amount, burn_time, int(time.time()), player_id, furnace_slot))
    else:
        cursor.execute(
            "UPDATE furnaces SET fuel_id_inside=%s, fuel_amount_inside=fuel_amount_inside+%s WHERE player_id=%s AND furnace_slot=%s;",
            (item_id, amount, player_id, furnace_slot))
    cursor.close()
    psql_conn.commit()


def add_item_in_furnace(player_id, item_id, amount, furnace_slot, set_time=0):
    cursor = psql_conn.cursor()

    if set_time:
        cursor.execute(
            "UPDATE furnaces SET item_id_inside=%s, item_amount_inside=item_amount_inside+%s, next_item_burn=%s  WHERE player_id=%s AND furnace_slot=%s;",
            (item_id, amount, set_time, player_id, furnace_slot))
    else:
        cursor.execute(
            "UPDATE furnaces SET item_id_inside=%s, item_amount_inside=item_amount_inside+%s WHERE player_id=%s AND furnace_slot=%s;",
            (item_id, amount, player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()


def remove_fuel(player_id, furnace_slot, from_finished=False):
    cursor = psql_conn.cursor()

    current_fuel_id, amount = 0, 0
    if not from_finished:
        from itemIDs_dictionaries import ITEMS
        current_fuel_id, amount, burn_time = get_current_fuel_in_furnace(player_id, furnace_slot)

        if burn_time != ITEMS[current_fuel_id]['fuel_power']:
            amount -= 1
        if amount:
            add_item(player_id, current_fuel_id, amount)

    cursor.execute(
        "UPDATE furnaces SET fuel_id_inside=0, fuel_amount_inside=0, next_fuel_burn=0 WHERE player_id=%s AND furnace_slot=%s;",
        (player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()

    return current_fuel_id, amount


def remove_fuel_with_amount(player_id, furnace_slot, amount_to_remove):
    cursor = psql_conn.cursor()

    from itemIDs_dictionaries import ITEMS
    current_fuel_id, amount_inside, burn_time = get_current_fuel_in_furnace(player_id, furnace_slot)
    original_item_inside = current_fuel_id

    if burn_time != ITEMS[current_fuel_id]['fuel_power']:
        amount_inside -= 1

    if amount_inside < amount_to_remove:
        amount_to_remove = amount_inside

    add_item(player_id, current_fuel_id, amount_to_remove)

    if amount_inside <= amount_to_remove:
        current_fuel_id = 0
        burn_time = 0

    cursor.execute("UPDATE furnaces SET "
                   "fuel_id_inside=%s,"
                   " fuel_amount_inside=fuel_amount_inside-%s,"
                   " next_fuel_burn=%s"
                   " WHERE player_id=%s AND furnace_slot=%s;",
                   (current_fuel_id, amount_to_remove, burn_time, player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()

    return original_item_inside, amount_to_remove


def remove_item_in_furnace(player_id, furnace_slot, from_finished=False):
    from itemIDs_dictionaries import ITEMS
    cursor = psql_conn.cursor()

    current_item_id, amount = 0, 0
    if not from_finished:
        current_item_id, amount = get_current_item_in_furnace(player_id, furnace_slot)
        for item_in_recipe, amount_in_recipe in ITEMS[current_item_id]['recipe']:
            add_item(player_id, item_in_recipe, amount_in_recipe * amount)

    cursor.execute(
        "UPDATE furnaces SET item_id_inside=0, item_amount_inside=0, next_item_burn=0 WHERE player_id=%s AND furnace_slot=%s;",
        (player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()

    return current_item_id, amount


def remove_done_item_in_furnace(player_id, furnace_slot, item_amount):
    cursor = psql_conn.cursor()

    cursor.execute(
        "UPDATE furnaces SET item_amount_inside=item_amount_inside-%s WHERE player_id=%s AND furnace_slot=%s;",
        (item_amount, player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()


def remove_done_fuel_in_furnace(player_id, furnace_slot, item_amount):
    cursor = psql_conn.cursor()

    cursor.execute(
        "UPDATE furnaces SET fuel_amount_inside=fuel_amount_inside-%s WHERE player_id=%s AND furnace_slot=%s;",
        (item_amount, player_id, furnace_slot))

    cursor.close()
    psql_conn.commit()


def get_furnaces_info(player_id, slot=-1):
    cursor = psql_conn.cursor()

    if slot >= 0:
        cursor.execute("SELECT * FROM furnaces WHERE player_id=%s AND furnace_slot=%s;", (player_id, slot))
    else:
        cursor.execute("SELECT * FROM furnaces WHERE player_id=%s;", (player_id,))

    furnaces = cursor.fetchall()

    furnace_dict = {}
    for _, furnace_item_id, furnace_slot, last_collected, item_to_smelt, item_amount, fuel_used, fuel_amount, last_fuel_burned, last_item_burned in furnaces:
        furnace_dict[furnace_slot] = {'furnace_id': furnace_item_id,
                                      'last_collected': last_collected,
                                      'item_inside': item_to_smelt,
                                      'item_amount_inside': item_amount,
                                      'fuel_inside': fuel_used,
                                      'fuel_amount': fuel_amount,
                                      'next_fuel': last_fuel_burned,
                                      'next_item': last_item_burned}

    return furnace_dict


def set_house(player_id, house_id):
    cursor = psql_conn.cursor()

    cursor.execute("DELETE FROM houses WHERE player_id=%s;", (player_id,))
    cursor.execute("INSERT INTO houses (player_id, house_id, is_owned) VALUES (%s, %s, %s);",
                   (player_id, house_id, 1))

    cursor.close()
    psql_conn.commit()


def add_pickaxe(player_id, pickaxe_id):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_gear SET pickaxe=%s WHERE player_id=%s;", (pickaxe_id, player_id))
    cursor.execute("INSERT INTO owned_pickaxes (player_id, pickaxe_id) VALUES (%s, %s);",
                   (player_id, pickaxe_id))

    cursor.close()
    psql_conn.commit()


def equip_pickaxe(player_id, pickaxe_id):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_gear SET pickaxe=%s WHERE player_id=%s;", (pickaxe_id, player_id))

    cursor.close()
    psql_conn.commit()


def get_all_owned_pickaxes(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT pickaxe_id FROM owned_pickaxes WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()


def get_all_owned_armors(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT armor_id FROM owned_armors WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()


def get_all_owned_helmets(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT helmet_id FROM owned_helmets WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()


def get_all_owned_weapons(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT weapon_id FROM owned_weapons WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()


def is_pickaxe_owned(player_id, pickaxe_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT pickaxe_id FROM owned_pickaxes WHERE player_id=%s AND pickaxe_id=%s;",
                   (player_id, pickaxe_id))

    return bool(cursor.fetchall())


def add_armor(player_id, armor_id, equip=True):
    cursor = psql_conn.cursor()

    if equip:
        cursor.execute("UPDATE player_gear SET chest=%s WHERE player_id=%s;", (armor_id, player_id))

    cursor.execute("INSERT INTO owned_armors (player_id, armor_id) VALUES (%s, %s);", (player_id, armor_id))
    cursor.close()
    psql_conn.commit()


def equip_armor(player_id, armor_id):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_gear SET chest=%s WHERE player_id=%s;", (armor_id, player_id))

    cursor.close()
    psql_conn.commit()


def is_armor_owned(player_id, armor_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT armor_id FROM owned_armors WHERE player_id=%s AND armor_id=%s;", (player_id, armor_id))

    return bool(cursor.fetchall())


def add_weapon(player_id, weapon_id, equip=True):
    cursor = psql_conn.cursor()

    if equip:
        cursor.execute("UPDATE player_gear SET weapon=%s WHERE player_id=%s;", (weapon_id, player_id))

    cursor.execute("INSERT INTO owned_weapons (player_id, weapon_id) VALUES (%s, %s);", (player_id, weapon_id))

    cursor.close()
    psql_conn.commit()


def equip_weapon(player_id, weapon_id):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_gear SET weapon=%s WHERE player_id=%s;", (weapon_id, player_id))

    cursor.close()
    psql_conn.commit()


def is_weapon_owned(player_id, weapon_id):
    cursor = psql_conn.cursor()

    cursor.execute("SELECT weapon_id FROM owned_weapons WHERE player_id=%s AND weapon_id=%s;", (player_id, weapon_id))

    return bool(cursor.fetchall())


def add_helmet(player_id, helmet_id, equip=True):
    cursor = psql_conn.cursor()

    if equip:
        cursor.execute("UPDATE player_gear SET helmet=%s WHERE player_id=%s;", (helmet_id, player_id))

    cursor.execute("INSERT INTO owned_helmets (player_id, helmet_id) VALUES (%s, %s);", (player_id, helmet_id))

    cursor.close()
    psql_conn.commit()


def is_helmet_owned(player_id, helmet_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT helmet_id FROM owned_helmets WHERE player_id=%s AND helmet_id=%s;", (player_id, helmet_id))

    return bool(cursor.fetchall())


def equip_helmet(player_id, helmet_id):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE player_gear SET helmet=%s WHERE player_id=%s;", (helmet_id, player_id))

    cursor.close()
    psql_conn.commit()


def add_station(player_id, station_id, slot_number):
    cursor = psql_conn.cursor()

    cursor.execute("INSERT INTO crafting_stations (player_id, station_id, slot_in_house) VALUES (%s, %s, %s);",
                   (player_id, station_id, slot_number))

    from itemIDs_dictionaries import CRAFTING_STATIONS
    if 'furnace' in CRAFTING_STATIONS[station_id]:
        cursor.execute("INSERT INTO furnaces (player_id, furnace_id, furnace_slot) VALUES (%s, %s, %s);",
                       (player_id, station_id, slot_number))

    cursor.close()
    psql_conn.commit()


def delete_station(player_id, station_id, slot_in_house):
    cursor = psql_conn.cursor()

    cursor.execute("DELETE FROM crafting_stations WHERE player_id=%s AND station_id=%s AND slot_in_house=%s;",
                   (player_id, station_id, slot_in_house))
    cursor.execute("DELETE FROM furnaces WHERE player_id=%s AND furnace_id=%s AND furnace_slot=%s;",
                   (player_id, station_id, slot_in_house))

    cursor.close()
    psql_conn.commit()


def get_available_crafting_stations_list(player_id):
    cursor = psql_conn.cursor()

    cursor.execute("SELECT * FROM crafting_stations WHERE player_id=%s;", (player_id,))

    return cursor.fetchall()


def get_player_house(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT house_id FROM houses WHERE player_id = %s AND is_owned=1;", (player_id,))

    house = cursor.fetchall()
    cursor.close()
    if not house:
        return 0

    return house[0][0]


def update_cooldown(player_id, command_id):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE cooldowns SET last_used=%s WHERE player_id=%s AND command_id=%s;",
                   (time.time(), player_id, command_id))
    cursor.close()


def update_cooldown_set(player_id, command_id, _time):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE cooldowns SET last_used=%s WHERE player_id=%s AND command_id=%s;",
                   (_time, player_id, command_id))
    cursor.close()


def get_all_cds(player_id):
    cursor = psql_conn.cursor()

    cursor.execute("SELECT last_used, command_id FROM cooldowns WHERE player_id=%s;", (player_id,))
    cooldown = cursor.fetchall()

    return cooldown


def get_cooldown(player_id, command_id):
    cursor = psql_conn.cursor()

    cursor.execute("SELECT last_used FROM cooldowns WHERE player_id=%s AND command_id=%s;", (player_id, command_id))
    cooldown = cursor.fetchone()

    if not cooldown:
        cursor.execute("INSERT INTO cooldowns (player_id, command_id, last_used) VALUES (%s, %s, %s);",
                       (player_id, command_id, 0))
        cursor.close()
        return 0

    else:
        cursor.close()
        return cooldown[0]


def get_full_inventory_dict(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT item_id, item_amount FROM inventory WHERE player_id=%s;", (player_id,))
    inventory = cursor.fetchall()

    if not inventory:
        return {}

    return {item: amount for item, amount in sorted(inventory, key=lambda x: x[0])}


def remove_item(player_id, item_id, amount_to_remove):
    cursor = psql_conn.cursor()

    cursor.execute("UPDATE inventory SET item_amount=item_amount-%s WHERE player_id=%s and item_id=%s;",
                   (amount_to_remove, player_id, item_id))

    cursor.close()
    psql_conn.commit()


def add_item(player_id, item_id, amount_to_add):
    cursor = psql_conn.cursor()

    cursor.execute("""
INSERT INTO inventory (player_id, item_id, item_amount)
VALUES (%s, %s, %s)
ON CONFLICT (player_id, item_id) DO
UPDATE SET item_amount = inventory.item_amount + %s WHERE inventory.player_id=%s and inventory.item_id=%s;""",
                   (player_id, item_id, amount_to_add, amount_to_add, player_id, item_id))

    cursor.close()
    psql_conn.commit()


def set_stat(player_id, stat_name_in_db, value):
    """Sets a stat"""
    cursor = psql_conn.cursor()
    cursor.execute(f"UPDATE player_stats SET {stat_name_in_db}=%s WHERE player_id=%s;", (value, player_id))

    cursor.close()
    psql_conn.commit()


async def get_all_player_info(channel, author, ping=0):
    """Returns all user stats, like HP, area, """
    cursor = psql_conn.cursor()
    cursor.execute("SELECT area, max_area, health, max_health, trait_points, current_xp, level, mana, max_mana FROM player_stats WHERE player_id=%s;", (author.id,))

    stats = cursor.fetchall()
    if not stats:
        if ping and ping != author.id:
            await channel.send(f"<@{ping}> That user never played before!")
        else:
            await channel.send(f"<@{author.id}> To start playing for the first time use `val begin`")

        return None

    cursor.close()

    return stats[0]


async def get_all_player_stats_battle(channel, player_id, ping=0):
    """Returns all user stats, like HP, area, """
    cursor = psql_conn.cursor()
    cursor.execute("SELECT area, health, max_health, level, current_xp, mana, max_mana  FROM player_stats WHERE player_id=%s;",
                   (player_id,))

    stats = cursor.fetchall()
    if not stats:
        if ping and ping != player_id:
            await channel.send(
                f"<@{ping}> You can't add <@{player_id}> to the party, because they never played before!")
        else:
            await channel.send(f"<@{player_id}> To start playing for the first time use `val begin`")

        return 0, 0, 0, 0, 0, 0, 0

    cursor.close()

    return stats[0]


async def get_player_area(channel, author, ping=0):
    try:
        if 'zone' in DATA_CACHE[author.id]:
            return DATA_CACHE[author.id]['zone']
    except KeyError:
        DATA_CACHE[author.id] = {'cmd': 0}
        pass

    cursor = psql_conn.cursor()
    cursor.execute("SELECT area FROM player_stats WHERE player_id=%s;", (author.id,))

    area = cursor.fetchall()
    cursor.close()

    if not area:
        if ping and ping != author.id:
            await channel.send(f"<@{ping}> That user never played before!")
        else:
            await channel.send(f"{author.mention} To start playing for the first time use `val begin`")
        return 0

    DATA_CACHE[author.id]['zone'] = area[0][0]

    return area[0][0]


async def get_player_max_area(channel, author, ping=0):
    try:
        if 'zone' in DATA_CACHE[author.id]:
            return DATA_CACHE[author.id]['zone'], DATA_CACHE[author.id]['max_zone']
    except KeyError:
        DATA_CACHE[author.id] = {'cmd': 0}
        pass

    cursor = psql_conn.cursor()
    cursor.execute("SELECT area, max_area FROM player_stats WHERE player_id=%s;", (author.id,))

    area = cursor.fetchall()
    cursor.close()

    if not area:
        if ping and ping != author.id:
            await channel.send(f"<@{ping}> That user never played before!")
        else:
            await channel.send(f"{author.mention} To start playing for the first time use `val begin`")
        return 0, 0

    if author.id in DATA_CACHE:
        DATA_CACHE[author.id]['zone'] = area[0][0]
        DATA_CACHE[author.id]['max_zone'] = area[0][1]

    return area[0]


async def get_player_pickaxe(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT pickaxe FROM player_gear WHERE player_id=%s;", (player_id,))

    item = cursor.fetchall()

    if not item:
        cursor.execute(f"INSERT INTO player_gear (player_id) VALUES (%s);", (player_id,))
        cursor.execute("SELECT pickaxe FROM player_gear WHERE player_id=%s;", (player_id,))
        item = cursor.fetchall()

    cursor.close()

    return item[0][0]


def get_all_player_gear(player_id):
    """Returns all the user's tools"""

    cursor = psql_conn.cursor()
    cursor.execute("SELECT pickaxe, weapon, helmet, chest FROM player_gear WHERE player_id=%s;", (player_id,))

    gear = cursor.fetchall()
    if not gear:
        cursor.execute(f"INSERT INTO player_gear (player_id) VALUES (%s);", (player_id,))
        return 0, 0, 0, 0

    cursor.close()
    return gear[0]


async def add_player_first_time(message):
    """Adds a user to the database if they never played before"""

    cursor = psql_conn.cursor()

    cursor.execute("SELECT player_id FROM player_stats WHERE player_id=%s;", (message.author.id,))

    if cursor.fetchone():
        await message.channel.send(
            f"<@{message.author.id}> You already began your journey! Use `val help` for more info!")
        cursor.close()
        return

    cursor.execute("INSERT INTO player_stats (player_id, area, health) VALUES (%s, %s, %s);",
                   (message.author.id, 1, 100))

    await message.channel.send(f"<@{message.author.id}> You where **instantly** teleported to an unknown location, to "
                               f"what seems to be a forest. Use `val help` for a list of... commands?")

    cursor.close()
    psql_conn.commit()


def set_hp(player_id, hp):
    cursor = psql_conn.cursor()
    cursor.execute("UPDATE player_stats SET health=%s WHERE player_id=%s;", (hp, player_id))

    cursor.close()
    psql_conn.commit()


def get_current_hp(player_id):
    cursor = psql_conn.cursor()
    cursor.execute("SELECT health, max_health FROM player_stats WHERE player_id=%s;", (player_id,))

    stats = cursor.fetchall()[0]
    return stats
