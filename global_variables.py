# For discord game bot
# IMPORT THIS IN ALL THE OTHER FILES!

# OTHER MODULES ========================================================================================================
import discord
import psycopg2

INTERACTION_BUCKET = dict()
VIEWS = {'base_select': None}

DATA_CACHE = dict()

NECROMANCER_ID = 557841939375063068

psql_conn = psycopg2.connect(database="discord_game_test_db", user="REPLACE_ME")

psql_conn.autocommit = True

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)
command_tree = discord.app_commands.CommandTree(bot)

