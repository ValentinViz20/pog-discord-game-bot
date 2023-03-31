import random


class MudGolemEnemy:
    def __init__(self, y, x):
        self.x = x
        self.y = y
        self.hp = random.randint(200, 250)
        self.at = 80
        self.effects = {}


def process_zone1_damage(player_info, boss_info, player_id, damage, effects_applied):
    X = player_info[player_id]['x']
    Y = player_info[player_id]['y']
    board = boss_info['board']

    # FRONT ==========================================
    if X < 9 and board[Y][X+1] == 1:
        boss_info['enemies'][f"{Y}{X + 1}"].hp -= damage

        if boss_info['enemies'][f"{Y}{X+1}"].hp <= 0:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** kills {BOSSES[1]['mud_golem']}!"
            del boss_info['enemies'][f"{Y}{X+1}"]
            board[Y][X+1] = 0
        else:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hits {BOSSES[1]['mud_golem']} ({boss_info['enemies'][f'{Y}{X+1}'].hp} HP left)!"

    elif X < 9 and board[Y][X+1] == 2:
        log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** is pushed back!"
        boss_info['hp'] -= damage
        y = random.randint(0, 3)
        x = 0
        while True:
            if not board[y][x] or x == 9:
                board[y][x] = player_id
                board[player_info[player_id]['y']][player_info[player_id]['x']] = 0
                player_info[player_id]['x'] = x
                player_info[player_id]['y'] = y
                break
            x += 1

    # BACK ==================================
    elif X and board[Y][X-1] == 1:
        boss_info['enemies'][f"{Y}{X - 1}"].hp -= damage

        if boss_info['enemies'][f"{Y}{X-1}"].hp <= 0:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** kills {BOSSES[1]['mud_golem']}!"
            del boss_info['enemies'][f"{Y}{X-1}"]
            board[Y][X - 1] = 0
        else:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hits {BOSSES[1]['mud_golem']} ({boss_info['enemies'][f'{Y}{X-1}'].hp} HP left)!"

    # UP ==========================================
    elif Y and board[Y-1][X] == 1:
        boss_info['enemies'][f"{Y-1}{X}"].hp -= damage

        if boss_info['enemies'][f"{Y-1}{X}"].hp <= 0:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** kills {BOSSES[1]['mud_golem']}!"
            del boss_info['enemies'][f"{Y-1}{X}"]
            board[Y-1][X] = 0
        else:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hits {BOSSES[1]['mud_golem']} ({boss_info['enemies'][f'{Y-1}{X}'].hp} HP left)!"

    elif Y and board[Y-1][X] == 2:
        log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** is pushed back!"
        boss_info['hp'] -= damage
        y = random.randint(0, 3)
        x = 0
        while True:
            if not board[y][x] or x == 9:
                board[y][x] = player_id
                board[player_info[player_id]['y']][player_info[player_id]['x']] = 0
                player_info[player_id]['x'] = x
                player_info[player_id]['y'] = y
                break
            x += 1

    # Down ==========================================
    elif Y < 3 and board[Y+1][X] == 1:
        boss_info['enemies'][f"{Y+1}{X}"].hp -= damage

        if boss_info['enemies'][f"{Y+1}{X}"].hp <= 0:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** kills {BOSSES[1]['mud_golem']}!"
            del boss_info['enemies'][f"{Y+1}{X}"]
            board[Y+1][X] = 0
        else:
            log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hits {BOSSES[1]['mud_golem']} ({boss_info['enemies'][f'{Y+1}{X}'].hp} HP left)!"

    elif Y < 3 and board[Y+1][X] == 2:
        log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** is pushed back!"
        boss_info['hp'] -= damage
        y = random.randint(0, 3)
        x = 0
        while True:
            if not board[y][x] or x == 9:
                board[y][x] = player_id
                board[player_info[player_id]['y']][player_info[player_id]['x']] = 0
                player_info[player_id]['x'] = x
                player_info[player_id]['y'] = y
                break
            x += 1

    else:
        log_msg = f"**{boss_info['turn']}| {player_info[player_id]['user'].name}** hits the air!"

    if boss_info['hp'] < 0:
        boss_info['hp'] = 0

    if effects_applied:
        for effect in effects_applied:
            boss_info['debuffs'][effect] = effects_applied[effect]

    return log_msg


def process_zone1_boss_move(player_info, boss_info, logs, player_id):
    board = boss_info['board']
    damaged_players = dict.fromkeys(player_info, 0)

    for enemy in boss_info['enemies'].copy():
        players_around_enemy = []
        X = boss_info['enemies'][enemy].x
        Y = boss_info['enemies'][enemy].y

        if Y and board[Y-1][X] in damaged_players:
            players_around_enemy.append(board[Y-1][X])

        if Y < 3 and board[Y+1][X] in damaged_players:
            players_around_enemy.append(board[Y+1][X])

        if X and board[Y][X-1] in damaged_players:
            players_around_enemy.append(board[Y][X-1])

        if X < 9 and board[Y][X+1] in damaged_players:
            players_around_enemy.append(board[Y][X+1])

        if players_around_enemy:
            damaged_players[random.choice(players_around_enemy)] += boss_info['enemies'][enemy].at
        else:
            move_towards = random.choice(tuple(player_info))

            if X and not board[Y][X-1] and abs((X - 1) - player_info[move_towards]['x']) < abs(X - player_info[move_towards]['x']):
                board[Y][X] = 0
                board[Y][X - 1] = 1
                boss_info['enemies'][enemy].x -= 1
                boss_info['enemies'][f"{Y}{X-1}"] = boss_info['enemies'].pop(enemy)

            elif X < 9 and not board[Y][X+1] and abs((X + 1) - player_info[move_towards]['x']) < abs(X - player_info[move_towards]['x']):
                board[Y][X] = 0
                board[Y][X + 1] = 1
                boss_info['enemies'][enemy].x += 1
                boss_info['enemies'][f"{Y}{X + 1}"] = boss_info['enemies'].pop(enemy)

            elif Y and not board[Y-1][X] and abs((Y - 1) - player_info[move_towards]['y']) <  abs(Y - player_info[move_towards]['y']):
                board[Y][X] = 0
                board[Y-1][X] = 1
                boss_info['enemies'][enemy].y -= 1
                boss_info['enemies'][f"{Y - 1}{X}"] = boss_info['enemies'].pop(enemy)

            elif Y < 3 and not board[Y+1][X] and abs((Y + 1) - player_info[move_towards]['y']) <  abs(Y - player_info[move_towards]['y']):
                board[Y][X] = 0
                board[Y + 1][X] = 1
                boss_info['enemies'][enemy].y += 1
                boss_info['enemies'][f"{Y + 1}{X}"] = boss_info['enemies'].pop(enemy)

    if random.randint(0, 100) <= 23:
        if not board[boss_info['y'] - 1][9]:
            boss_info['enemies'][f"{boss_info['y'] - 1}{9}"] = MudGolemEnemy(boss_info['y'] - 1, 9)
            board[boss_info['y'] - 1][9] = 1

        elif not board[boss_info['y'] + 1][9]:
            boss_info['enemies'][f"{boss_info['y'] + 1}{9}"] = MudGolemEnemy(boss_info['y'] + 1, 9)
            board[boss_info['y'] + 1][9] = 1

        elif not board[boss_info['y']][8]:
            boss_info['enemies'][f"{boss_info['y']}{8}"] = MudGolemEnemy(boss_info['y'], 8)
            board[boss_info['y']][8] = 1

    for player, damage in damaged_players.items():
        if not damage:
            return

        damage -= (player_info[player_id]['def'] + player_info[player_id]["bonus"]['def'])
        if damage < 3:
            damage = random.randint(1, 3)

        logs.appendleft(f"**{boss_info['turn']}| {BOSSES[1]['mud_golem']} hit {player_info[player_id]['user'].name}** for {damage}!")
        player_info[player]['hp'] -= damage
        if player_info[player]['hp'] < 0:
            player_info[player]['hp'] = 0

    if boss_info['debuffs']:
        if 'on_fire' in boss_info['debuffs']:
            boss_info['debuffs']['on_fire'][0] -= 1

            for enemy in boss_info['enemies']:
                boss_info['enemies'][enemy].hp -= boss_info['debuffs']['on_fire'][1]

            logs.appendleft(f"**{boss_info['turn']}|** The fire deals **{boss_info['debuffs']['on_fire'][1]} damage** to ALL {BOSSES[1]['mud_golem']}!")

            if not boss_info['debuffs']['on_fire'][0]:
                del boss_info['debuffs']['on_fire']


def get_boss_map(player_info, boss_info):
    if boss_info['id'] == 6:
        board_text = ""
        for i, row in enumerate(boss_info['board']):
            for j, title in enumerate(row):
                if title in player_info:
                    board_text += player_info[title]['emoji']
                elif title == 1:
                    board_text += BOSSES[1]['mud_golem']
                elif title == 2:
                    board_text += BOSSES[1]['mud_golem_spawner']
                else:
                    board_text += "🟫"

            board_text += '\n'

        return board_text


def init_zone1_board(player_info, boss_info):
    boss_info['board'] = [[0 for _ in range(10)] for _ in range(4)]
    for player in player_info:
        boss_info['board'][player_info[player]['y']][player_info[player]['x']] = player

    boss_y = random.randint(1, 2)

    boss_info['board'][boss_y][9] = 2
    boss_info['x'] = 9
    boss_info['y'] = boss_y

    boss_info['enemies'] = {f"{boss_y - 1}{9}": MudGolemEnemy(boss_y - 1, 9),
                            f"{boss_y + 1}{9}": MudGolemEnemy(boss_y + 1, 9),
                            f"{boss_y}{8}": MudGolemEnemy(boss_y, 8)}
    boss_info['board'][boss_y - 1][9] = 1
    boss_info['board'][boss_y + 1][9] = 1
    boss_info['board'][boss_y][8] = 1


def process_zone1_actions(player_info, boss_info, custom_id, player_id):
    if custom_id == 'up_bt':
        X = player_info[player_id]['x']
        Y = player_info[player_id]['y']

        boss_info['board'][Y][X] = 0
        player_info[player_id]['y'] -= 1
        boss_info['board'][Y-1][X] = player_id

    elif custom_id == 'left_bt':
        X = player_info[player_id]['x']
        Y = player_info[player_id]['y']
        boss_info['board'][Y][X] = 0
        player_info[player_id]['x'] -= 1
        boss_info['board'][Y][X-1] = player_id

    elif custom_id == 'right_bt':
        X = player_info[player_id]['x']
        Y = player_info[player_id]['y']

        boss_info['board'][Y][X] = 0
        player_info[player_id]['x'] += 1
        boss_info['board'][Y][X+1] = player_id

    elif custom_id == 'down_bt':
        X = player_info[player_id]['x']
        Y = player_info[player_id]['y']

        boss_info['board'][Y][X] = 0
        player_info[player_id]['y'] += 1
        boss_info['board'][Y+1][X] = player_id

    player_info[player_id]['turn_left'] -= 1


BOSSES = {
    1: {'mud_golem': '<:mud_golem2:1026151434745557033>', 'mud_golem_spawner': '<:mud_golem_spawner:1026094289723334747>',
        'max_y': 3, 'max_x': 9, 'get_board': (4, 10),
        'board_init': init_zone1_board,
        'button_actions': process_zone1_actions,
        'damage_handler': process_zone1_damage,
        'move_processor': process_zone1_boss_move,
        'map_getter': get_boss_map}
}