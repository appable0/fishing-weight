import hikari
import lightbulb
import requests
import os
import json
import math
from functions import get_player_fishing_level
from functions import determine_dolphin_rarity, get_dolphin_ms_weight, format_pet_name

bot = lightbulb.BotApp(
    token='Discord Bot Token', 
    default_enabled_guilds=('Allowed Discord Server IDs')
)

@bot.command
@lightbulb.option('ign', 'in game name', type=str)
@lightbulb.command('fishing_weight', 'Gathers profile fishing weight given a valid IGN')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    
    IGN = ctx.options.ign

    import requests
    import os
    import json
    import math
    from functions import get_player_fishing_level
    from functions import determine_dolphin_rarity, get_dolphin_ms_weight, format_pet_name


    def dumpJsonFile(json_data, nameOfFile):
        with open(nameOfFile, 'w', encoding='utf-8') as written_file:
            json.dump(json_data, written_file, indent=4)

    # PLAYER UUID
    uuid_url = 'https://api.mojang.com/users/profiles/minecraft/' + IGN
    uuid_response = requests.get(uuid_url)
    uuid_json = uuid_response.json()
    uuid_ign = uuid_json['id']
    # print(uuid_ign)


    # DEV KEY 
    files = os.listdir()
    if 'key.txt' in files: 
        key_path = os.path.join(os.getcwd(), 'key.txt')
        with open(key_path, 'r', encoding='utf-8') as key_file:
            dev_key = key_file.readline().strip()


    # API 
    api_url = 'https://api.hypixel.net/v2/skyblock/profiles?uuid=' + uuid_ign + "&key=" + dev_key + '&profile'
    api_response = requests.get(api_url)
    api_json = api_response.json()

    dumpJsonFile(api_json, './json/api_response.json')


    # GET PLAYER API DATA
    api_profiles = api_json['profiles']
    for profile in api_profiles:
        selected = profile['selected']
        player_profile_name = profile['cute_name']
        if selected:
            profile_info = profile['members'][uuid_ign]
            if profile_info:
                # player_id = profile_info['player_id']
                player_data = profile_info['player_data']
                player_leveling = profile_info['leveling']
                player_bestiary_info = profile_info['bestiary']
                player_stats = profile_info['player_stats']
                player_tfish_stats = profile_info['trophy_fish']
                # player_inventory = profile_info['inventory']
                player_collection = profile_info['collection']
                player_pet_data = profile_info['pets_data']['pets']

    #if player_data:
    #    player_crafted_minions = player_data['crafted_generators']

    # if player_inventory:
    #     player_bags = player_inventory['bag_contents']

    if player_bestiary_info:
        player_be_deaths = player_bestiary_info['deaths']
        player_be_kills = player_bestiary_info['kills']


    # dumps
    # dumpJsonFile(player_collection, './json/player_collections.json')
    # dumpJsonFile(player_crafted_minions, './json/player_minions.json')
    # dumpJsonFile(player_be_kills, './json/player_be_kills.json')
    # dumpJsonFile(player_be_deaths, './json/player_be_deaths.json')
    # dumpJsonFile(player_tfish_stats, './json/player_tfish_stats.json')
    # dumpJsonFile(player_stats, './json/player_stats.json')

    # fishing skill 
    LEVEL_50_EXP = 55172425
    LEVEL_60_EXP = 111672425

    SKILL_EXP_VALUES = {
        0: 0, 
        1: 50, 
        2: 175, 
        3: 375,
        4: 675, 
        5: 1175, 
        6: 1925, 
        7: 2925, 
        8: 4425, 
        9: 6425, 
        10: 9925, 
        11: 14925, 
        12: 22425, 
        13: 32425, 
        14: 47425, 
        15: 67425, 
        16: 97425, 
        17: 147425, 
        18: 222425, 
        19: 322425, 
        20: 522425, 
        21: 822425, 
        22: 1222425, 
        23: 1722425, 
        24: 2322425, 
        25: 3022425, 
        26: 3822425, 
        27: 4722425, 
        28: 5722425, 
        29: 6822425, 
        30: 8022425, 
        31: 9322425, 
        32: 10722425, 
        33: 12222425, 
        34: 13822425, 
        35: 15522425, 
        36: 17322425, 
        37: 19222425, 
        38: 21222425, 
        39: 23322425, 
        40: 25522425, 
        41: 27822425, 
        42: 30222425, 
        43: 32722425, 
        44: 35322425, 
        45: 38072425, 
        46: 40972425, 
        47: 44072425, 
        48: 47472425,
        49: 51172425,
        50: 55172425,
        51: 59472425, 
        52: 64072425, 
        53: 68972425, 
        54: 74172425, 
        55: 79672425, 
        56: 85472425, 
        57: 91572425, 
        58: 97972425, 
        59: 104672425, 
        60: 111672425
    }

    fishing_treasure_caught = player_data['fishing_treasure_caught']
    fishing_skill_exp = player_data['experience']['SKILL_FISHING']
    overflow_fishing_exp = fishing_skill_exp - LEVEL_60_EXP
    if (overflow_fishing_exp<=0): overflow_fishing_exp = 0
    player_fishing_level = get_player_fishing_level(fishing_skill_exp, SKILL_EXP_VALUES)


    # fishing exp
    def getFishingExpWeight(lvl, overflow):
        return round(((lvl / 50) * 2500))

    def getFishingExpOverflowWeight(lvl, overflow):
        if round((10 * math.sqrt((overflow / 60000000) * 10000) - 750)) < 0:
            return 0
        return round((10 * math.sqrt((overflow / 60000000) * 10000) - 750))


    total_fexp_weight = getFishingExpWeight(player_fishing_level, overflow_fishing_exp)
    total_fexp_overflow_weight = getFishingExpOverflowWeight(player_fishing_level, overflow_fishing_exp)


    # bestiary kills
    # note: not using deaths or k/d ratios
    class MobCollection:
        def __init__(self, name, api_name1, api_name2, max_be_kills, catch_chance, scalar, max_ms_weight):
            self.name = name
            self.api_name1 = api_name1
            self.api_name2 = api_name2
            self.kills = Mob.getKills(self.api_name1) + Mob.getKills(self.api_name2)
            self.deaths = Mob.getDeaths(self.api_name1) + Mob.getDeaths(self.api_name2)
            self.kd = Mob.calculate_kd(self.kills, self.deaths)
            self.max_be_kills = max_be_kills
            self.maxed_be_bool = Mob.isBestiaryCompleted(self.kills, self.max_be_kills)
            self.progress_be = Mob.getBestiaryProgress(self.kills, self.max_be_kills)
            self.catch_chance = Mob.percent(catch_chance)
            self.scalar = scalar
            self.max_ms_weight = max_ms_weight
            self.mob_weight = Mob.calculate_sc_weight(self)
            self.mob_overflow_weight = Mob.calculate_sc_overflow_weight(self)

    class Mob:
        def __init__(self, name, api_name, max_be_kills, catch_chance, scalar, max_ms_weight):
            self.name = name
            self.api_name = api_name
            self.kills = Mob.getKills(self.api_name)
            self.deaths = Mob.getDeaths(self.api_name)
            self.kd = Mob.calculate_kd(self.kills, self.deaths)
            self.max_be_kills = max_be_kills
            self.maxed_be_bool = Mob.isBestiaryCompleted(self.kills, self.max_be_kills)
            self.progress_be = Mob.getBestiaryProgress(self.kills, self.max_be_kills)
            self.catch_chance = Mob.percent(catch_chance)
            self.scalar = scalar
            self.max_ms_weight = max_ms_weight
            self.mob_weight = Mob.calculate_sc_weight(self)
            self.mob_overflow_weight = Mob.calculate_sc_overflow_weight(self)
        
        @staticmethod
        def calculate_kd(kills, death):
            return round(kills / death, 2) if death != 0.00 else 'undefined'

        @staticmethod
        def percent(part):
            return float(100 * float(part) / float(100))
        
        @staticmethod
        def getKills(info_name):
            return player_be_kills.get(info_name, 0.00)
        
        @staticmethod
        def getDeaths(info_name):
            return player_be_deaths.get(info_name, 0.00)
        
        @staticmethod
        def isBestiaryCompleted(kills, max_kills):
            if (kills >= max_kills): return True
            else: return False

        @staticmethod
        def getBestiaryProgress(kills, max_kills):
            return min(1, kills / max_kills)
        
        @staticmethod
        def calculate_sc_overflow_weight(self):
            CATCH_TIME = 4
            sc_weight = (self.catch_chance * 3600) / CATCH_TIME
            overflow_kills = self.kills - self.max_be_kills
            
            if overflow_kills <= 0: 
                overflow_weight = 0
            else:
                overflow_weight = 2 * math.sqrt(((overflow_kills / self.max_be_kills) * sc_weight) / self.scalar) -25
                if overflow_weight < 0:
                    overflow_weight = (((overflow_kills / self.max_be_kills) * sc_weight) / self.scalar)/25
            
            return round(overflow_weight)
        
        @staticmethod
        def calculate_sc_weight(self):
            CATCH_TIME = 4
            ms_weight = self.progress_be * float(self.max_ms_weight)
            
            return round(ms_weight)
        

    sea_creatures = {
        'water_family': {
            'agarimoo': Mob(name = 'agarimoo', api_name = 'agarimoo_35', max_be_kills = 4000, catch_chance = 16.31, scalar = 60, max_ms_weight = 36.7), 
            'carrot_king': Mob(name = 'carrot_king', api_name = 'carrot_king_25', max_be_kills = 400, catch_chance = 5.76, scalar = 12, max_ms_weight = 64.8), 
            'catfish': Mob(name='catfish', api_name='catfish_23', max_be_kills=1000, catch_chance=5.10, scalar=20, max_ms_weight=34.4),
            'deep_sea_protector': Mob(name='deep_sea_protector', api_name='deep_sea_protector_60', max_be_kills=1000, catch_chance=1.79, scalar=8, max_ms_weight=30.2),
            'guardian_defender': Mob(name='guardian_defender', api_name='guardian_defender_45', max_be_kills=1000, catch_chance=2.65, scalar=6, max_ms_weight=59.6),
            'night_squid': Mob(name='night_squid', api_name='night_squid_6', max_be_kills=1000, catch_chance=17.85, scalar=40, max_ms_weight=60.2),
            'oasis_rabbit': Mob(name='oasis_rabbit', api_name='oasis_rabbit_10', max_be_kills=300, catch_chance=5.08, scalar=10, max_ms_weight=68.6),
            'oasis_sheep': Mob(name='oasis_sheep', api_name='oasis_sheep_10', max_be_kills=300, catch_chance=11.85, scalar=30, max_ms_weight=53.3),
            'poisoned_water_worm': Mob(name='poisoned_water_worm', api_name='poisoned_water_worm_25', max_be_kills=1000, catch_chance=50.00, scalar=200, max_ms_weight=33.8),
            'rider_of_the_deep': MobCollection(name='rider_of_the_deep', api_name1='chicken_deep_20', api_name2='zombie_deep_20', max_be_kills=4000, catch_chance=8.15, scalar=40, max_ms_weight=27.5),
            'sea_archer': Mob(name='sea_archer', api_name='sea_archer_15', max_be_kills=4000, catch_chance=8.15, scalar=50, max_ms_weight=30.3),
            'sea_guardian': Mob(name='sea_guardian', api_name='sea_guardian_10', max_be_kills=4000, catch_chance=12.23, scalar=50, max_ms_weight=33.0),
            'sea_leech': Mob(name='sea_leech', api_name='sea_leech_30', max_be_kills=1000, catch_chance=3.26, scalar=11.5, max_ms_weight=38.3),
            'sea_walker': Mob(name='sea_walker', api_name='sea_walker_4', max_be_kills=4000, catch_chance=16.31, scalar=80, max_ms_weight=27.5),
            'sea_witch': Mob(name='sea_witch', api_name='sea_witch_15', max_be_kills=4000, catch_chance=14.27, scalar=70, max_ms_weight=27.5),
            'squid': Mob(name='squid', api_name='pond_squid_1', max_be_kills=10000, catch_chance=24.56, scalar=7.5, max_ms_weight=50),
            'sea_emperor': MobCollection(name='sea_emperor', api_name1='guardian_emperor_150', api_name2='skeleton_emperor_150', max_be_kills=100, catch_chance=0.24, scalar=0.5, max_ms_weight=64.8),
            'water_hydra': Mob(name='water_hydra', api_name='water_hydra_100', max_be_kills=400, catch_chance=0.44, scalar=1, max_ms_weight=59.9),
            'water_worm': Mob(name='water_worm', api_name='water_worm_20', max_be_kills=1000, catch_chance=50.00, scalar=200, max_ms_weight=33.8),
            'zombie_miner': Mob(name='zombie_miner', api_name='zombie_miner_150', max_be_kills=250, catch_chance=10.91, scalar=24, max_ms_weight=61.4)
        }, 
        'lava_family': {
            'fire_eel': Mob(name='fire_eel', api_name='fire_eel_240', max_be_kills=1000, catch_chance=6.08, scalar=8.25, max_ms_weight=27.5),
            'flaming_worm': Mob(name='flaming_worm', api_name='flaming_worm_50', max_be_kills=4000, catch_chance=100.00, scalar=350, max_ms_weight=97.7),
            'lava_blaze': Mob(name='lava_blaze', api_name='lava_blaze_100', max_be_kills=1000, catch_chance=50.00, scalar=68, max_ms_weight=99.5),
            'lava_flame': Mob(name='lava_flame', api_name='lava_flame_230', max_be_kills=1000, catch_chance=6.94, scalar=14, max_ms_weight=38.6),
            'lava_leech': Mob(name='lava_leech', api_name='lava_leech_220', max_be_kills=4000, catch_chance=13.02, scalar=18, max_ms_weight=99.3),
            'lava_pigman': Mob(name='lava_pigman', api_name='lava_pigman_100', max_be_kills=1000, catch_chance=50.00, scalar=200, max_ms_weight=66.9),
            'lord_jawbus': Mob(name='lord_jawbus', api_name='lord_jawbus_600', max_be_kills=250, catch_chance=0.20, scalar=0.25, max_ms_weight=97.7),
            'magma_slug': Mob(name='magma_slug', api_name='magma_slug_200', max_be_kills=10000, catch_chance=34.72, scalar=50, max_ms_weight=104.1),
            'moogma': Mob(name='moogma', api_name='moogma_210', max_be_kills=4000, catch_chance=26.04, scalar=36, max_ms_weight=108.4),
            'plhlegblast': Mob(name='plhlegblast', api_name='pond_squid_300', max_be_kills=7, catch_chance=0.12, scalar=0.2, max_ms_weight=141.4),
            'pyroclastic_worm': Mob(name='pyroclastic_worm', api_name='pyroclastic_worm_240', max_be_kills=4000, catch_chance=8.68, scalar=12, max_ms_weight=136.0),
            'taurus': Mob(name='taurus', api_name='pig_rider_250', max_be_kills=1000, catch_chance=3.47, scalar=4.5, max_ms_weight=137.6),
            'thunder': Mob(name='thunder', api_name='thunder_400', max_be_kills=400, catch_chance=1.04, scalar=1.3, max_ms_weight=148.5)
        }, 
        'spooky_family': {
            'scarecrow': Mob(name='scarecrow', api_name='scarecrow_9', max_be_kills=4000, catch_chance=14.66, scalar=14, max_ms_weight=166.5),
            'nightmare': Mob(name='nightmare', api_name='nightmare_24', max_be_kills=1000, catch_chance=8.06, scalar=8, max_ms_weight=151.4),
            'werewolf': Mob(name='werewolf', api_name='werewolf_50', max_be_kills=1000, catch_chance=3.67, scalar=3.6, max_ms_weight=151.4),
            'phantom_fisherman': Mob(name='phantom_fisherman', api_name='phantom_fisherman_160', max_be_kills=250, catch_chance=1.32, scalar=1.2, max_ms_weight=152.1),
            'grim_reaper': Mob(name='grim_reaper', api_name='grim_reaper_190', max_be_kills=100, catch_chance=0.37, scalar=0.3, max_ms_weight=156.2)
        }, 
        'shark_family': {
            'nurse_shark': Mob(name='nurse_shark', api_name='nurse_shark_6', max_be_kills=4000, catch_chance=15.70, scalar=14, max_ms_weight=165.1),
            'blue_shark': Mob(name='blue_shark', api_name='blue_shark_20', max_be_kills=1000, catch_chance=7.85, scalar=7, max_ms_weight=154.0),
            'tiger_shark': Mob(name='tiger_shark', api_name='tiger_shark_50', max_be_kills=1000, catch_chance=4.28, scalar=3.8, max_ms_weight=164.3),
            'great_white_shark': Mob(name='great_white_shark', api_name='great_white_shark_180', max_be_kills=400, catch_chance=2.14, scalar=1.85, max_ms_weight=165.5)
        }, 
        'winter_family': {
            'frosty': Mob(name='frosty', api_name='frosty_the_snowman_13', max_be_kills=4000, catch_chance=11.62, scalar=9.5, max_ms_weight=168.8),
            'frozen_steve': Mob(name='frozen_steve', api_name='frozen_steve_7', max_be_kills=4000, catch_chance=15.97, scalar=14, max_ms_weight=165.0),
            'grinch': Mob(name='grinch', api_name='grinch_21', max_be_kills=250, catch_chance=0.73, scalar=0.6, max_ms_weight=168.8),
            'nutcracker': Mob(name='nutcracker', api_name='nutcracker_50', max_be_kills=400, catch_chance=0.76, scalar=0.62, max_ms_weight=165.0),
            'reindrake': Mob(name='reindrake', api_name='reindrake_100', max_be_kills=100, catch_chance=0.05, scalar=0.04, max_ms_weight=165.0),
            'yeti': Mob(name='yeti', api_name='yeti_175', max_be_kills=250, catch_chance=0.44, scalar=0.36, max_ms_weight=165.0)
        }
    }

    for mob_key, mob_value in sea_creatures.items():
        if mob_key == 'water_family':
            water_family_weight = sum(mobObject.mob_weight for mobObject in mob_value.values())
            water_family_overflow_weight = sum(mobObject.mob_overflow_weight for mobObject in mob_value.values())
        if mob_key == 'lava_family':
            lava_family_weight = sum(mobObject.mob_weight for mobObject in mob_value.values())
            lava_family_overflow_weight = sum(mobObject.mob_overflow_weight for mobObject in mob_value.values())

        if mob_key == 'spooky_family': 
            spooky_family_weight = sum(mobObject.mob_weight for mobObject in mob_value.values())
            spooky_family_overflow_weight = sum(mobObject.mob_overflow_weight for mobObject in mob_value.values())

        if mob_key == 'shark_family': 
            shark_family_weight = sum(mobObject.mob_weight for mobObject in mob_value.values())
            shark_family_overflow_weight = sum(mobObject.mob_overflow_weight for mobObject in mob_value.values())

        if mob_key == 'winter_family':
            winter_family_weight = sum(mobObject.mob_weight for mobObject in mob_value.values())
            winter_family_overflow_weight = sum(mobObject.mob_overflow_weight for mobObject in mob_value.values())


    total_bestiary_weight = sum([water_family_weight, lava_family_weight, spooky_family_weight, shark_family_weight, winter_family_weight])
    total_bestiary_overflow_weight = sum([water_family_overflow_weight, lava_family_overflow_weight, spooky_family_overflow_weight, shark_family_overflow_weight, winter_family_overflow_weight])

    # collections
    class Collection:
        def __init__(self, name, max_coll, weight_per_item):
            self.name = name
            self.curr_coll = Collection.getCollection(self.name)
            self.max_coll = max_coll
            self.weight_per_item = weight_per_item
            self.progress_coll = Collection.calculate_collection_progress(self.curr_coll, self.max_coll)
            self.weight = Collection.calculate_collection_weight(self.progress_coll, self.weight_per_item)

        @staticmethod
        def getCollection(coll_name):
            return player_collection[coll_name]
        
        @staticmethod
        def calculate_collection_progress(coll, max_coll_value):
            return min(1, coll / max_coll_value)
        
        @staticmethod
        def calculate_collection_weight(progress, weight_per):
            return round(progress * weight_per)

    all_collections = {
        'clay': Collection(name='CLAY_BALL', max_coll=2500, weight_per_item=5), 
        'clownfish': Collection(name='RAW_FISH:2', max_coll=4000, weight_per_item=5), 
        'ink': Collection(name='INK_SACK', max_coll=4000, weight_per_item=5), 
        'lilypad': Collection(name='WATER_LILY', max_coll=10000, weight_per_item=5), 
        'magmafish': Collection(name='MAGMA_FISH', max_coll=500000, weight_per_item=50), 
        'prismarine_crystals': Collection(name='PRISMARINE_CRYSTALS', max_coll=800, weight_per_item=5), 
        'prismarine_shards': Collection(name='PRISMARINE_SHARD', max_coll=800, weight_per_item=5), 
        'pufferfish': Collection(name='RAW_FISH:3', max_coll=18000, weight_per_item=5), 
        'raw_fish': Collection(name='RAW_FISH', max_coll=60000, weight_per_item=5), 
        'raw_salmon': Collection(name='RAW_FISH:1', max_coll=10000, weight_per_item=5), 
        'sponge': Collection(name='SPONGE', max_coll=4000, weight_per_item=5)
    }

    total_collection_weight = round(sum(coll_object.weight for coll_object in all_collections.values()))


    # minions

    #class Minion:
    #    def __init__(self, name, tier):
    #        self.name = name
    #        self.tier = tier


    #player_best_minions = {}
    #for minion in player_crafted_minions:
    #    name_parts = minion.split('_')
    #    minion_name = format_pet_name(''.join(name_parts[:-1]))
    #    minion_tier = int(name_parts[-1])
    #    if minion_name not in player_best_minions or minion_tier > player_best_minions[minion_name].tier:
    #        player_best_minions[minion_name] = Minion(minion_name, minion_tier)

    # for k, v in player_best_minions.items():
    #     print(f'{k}: {v.name}, {v.tier}')


    # tfish
    class Tfishi:
        def __init__(self, name, catch_chance, bronze_scalar, silver_scalar, gold_scalar, diamond_scalar):
            self.name = name
            self.total = Tfishi.getTotalFishi(self.name)
            self.catch_chance = catch_chance
            self.bronze = Tfishi.getBronzeFishi(self.name)
            self.silver = Tfishi.getSilverFishi(self.name)
            self.gold = Tfishi.getGoldFishi(self.name)
            self.diamond = Tfishi.getDiamondFishi(self.name)
            self.bronze_scalar = bronze_scalar
            self.silver_scalar = silver_scalar
            self.gold_scalar = gold_scalar
            self.diamond_scalar = diamond_scalar
            self.weight = Tfishi.calculate_tfishi_weight(self)
            self.tfish_overflow_weight = Tfishi.calculate_tfishi_overflow_weight(self)

        @staticmethod
        def getTotalFishi(name):
            return player_tfish_stats.get(name, 0)
        
        @staticmethod
        def getBronzeFishi(name):
            return player_tfish_stats.get(f'{name}_bronze', 0)
        
        @staticmethod
        def getSilverFishi(name):
            return player_tfish_stats.get(f'{name}_silver', 0)

        @staticmethod
        def getGoldFishi(name):
            return player_tfish_stats.get(f'{name}_gold', 0)
        
        @staticmethod
        def getDiamondFishi(name):
            return player_tfish_stats.get(f'{name}_diamond', 0)
        
        @staticmethod
        def calculate_tfishi_rarity_weight(rarity, chance, rarity_scalar):
            if rarity >= 1: return round(rarity_scalar * (1130/122114))
            else: return 0

        @staticmethod
        def calculate_tfishi_rarity_overflow_weight(rarity, chance, rarity_scalar):
            if rarity > 1: return round((0.15 * math.sqrt((rarity - 1) / (1 / rarity_scalar))))
            else: return 0
            

        @staticmethod
        def calculate_tfishi_weight(info):
            bronze_weight = Tfishi.calculate_tfishi_rarity_weight(info.bronze, info.catch_chance, info.bronze_scalar)
            silver_weight = Tfishi.calculate_tfishi_rarity_weight(info.silver, info.catch_chance, info.silver_scalar)
            gold_weight = Tfishi.calculate_tfishi_rarity_weight(info.gold, info.catch_chance, info.gold_scalar)
            diamond_weight = Tfishi.calculate_tfishi_rarity_weight(info.diamond, info.catch_chance, info.diamond_scalar)
            total_weight = round(bronze_weight + silver_weight + gold_weight + diamond_weight)
            return total_weight
        
        @staticmethod
        def calculate_tfishi_overflow_weight(info):
            bronze_weight = Tfishi.calculate_tfishi_rarity_overflow_weight(info.bronze, info.catch_chance, info.bronze_scalar)
            silver_weight = Tfishi.calculate_tfishi_rarity_overflow_weight(info.silver, info.catch_chance, info.silver_scalar)
            gold_weight = Tfishi.calculate_tfishi_rarity_overflow_weight(info.gold, info.catch_chance, info.gold_scalar)
            diamond_weight = Tfishi.calculate_tfishi_rarity_overflow_weight(info.diamond, info.catch_chance, info.diamond_scalar)
            total_overflow_weight = round(bronze_weight + silver_weight + gold_weight + diamond_weight)
            return total_overflow_weight
        
    all_tfish = {
        'steaming_hot_flounder': Tfishi(name='steaming_hot_flounder', catch_chance=0.2, bronze_scalar=5, silver_scalar=13, gold_scalar=110, diamond_scalar=380),
        'gusher': Tfishi(name='gusher', catch_chance=0.2, bronze_scalar=8, silver_scalar=20, gold_scalar=170, diamond_scalar=600),
        'blobfish': Tfishi(name='blobfish', catch_chance=0.15, bronze_scalar=8, silver_scalar=20, gold_scalar=170, diamond_scalar=600),
        'obfuscated_fish_2': Tfishi(name='obfuscated_fish_2', catch_chance=0.2, bronze_scalar=22, silver_scalar=55, gold_scalar=480, diamond_scalar=1700),
        'slugfish': Tfishi(name='slugfish', catch_chance=0.1, bronze_scalar=145, silver_scalar=360, gold_scalar=3200, diamond_scalar=11000),
        'flyfish': Tfishi(name='flyfish', catch_chance=0.08, bronze_scalar=8, silver_scalar=20, gold_scalar=170, diamond_scalar=600),
        'obfuscated_fish_3': Tfishi(name='obfuscated_fish_3', catch_chance=0.1, bronze_scalar=40, silver_scalar=100, gold_scalar=870, diamond_scalar=3000),
        'lava_horse': Tfishi(name='lava_horse', catch_chance=0.04, bronze_scalar=32, silver_scalar=80, gold_scalar=700, diamond_scalar=2400),
        'mana_ray': Tfishi(name='mana_ray', catch_chance=0.02, bronze_scalar=40, silver_scalar=100, gold_scalar=870, diamond_scalar=3000),
        'volcanic_stonefish': Tfishi(name='volcanic_stonefish', catch_chance=0.03, bronze_scalar=16, silver_scalar=40, gold_scalar=350, diamond_scalar=1200),
        'vanille': Tfishi(name='vanille', catch_chance=0.03, bronze_scalar=90, silver_scalar=225, gold_scalar=2000, diamond_scalar=6800),
        'skeleton_fish': Tfishi(name='skeleton_fish', catch_chance=0.02, bronze_scalar=80, silver_scalar=200, gold_scalar=1700, diamond_scalar=6000),
        'moldfin': Tfishi(name='moldfin', catch_chance=0.02, bronze_scalar=80, silver_scalar=200, gold_scalar=1700, diamond_scalar=6000),
        'soul_fish': Tfishi(name='soul_fish', catch_chance=0.02, bronze_scalar=80, silver_scalar=200, gold_scalar=1700, diamond_scalar=6000),
        'karate_fish': Tfishi(name='karate_fish', catch_chance=0.01, bronze_scalar=160, silver_scalar=400, gold_scalar=3500, diamond_scalar=12000),
        'golden_fish': Tfishi(name='golden_fish', catch_chance=0.005, bronze_scalar=400, silver_scalar=1000, gold_scalar=8700, diamond_scalar=30000),
        'sulphur_skitter': Tfishi(name='sulphur_skitter', catch_chance=0.3, bronze_scalar=2, silver_scalar=5, gold_scalar=40, diamond_scalar=150),
        'obfuscated_fish_1': Tfishi(name='obfuscated_fish_1', catch_chance=0.25, bronze_scalar=0.01, silver_scalar=0.02, gold_scalar=0.05, diamond_scalar=0.1),
    }

    total_tfishi_weight = sum(tfishi_object.weight for tfishi_object in all_tfish.values())
    total_tfishi_overflow_weight = sum(tfishi_object.tfish_overflow_weight for tfishi_object in all_tfish.values())

    # for key, value in all_tfish.items():
    #     print(key, value.name, value.weight)

    items_fished = player_stats['items_fished']
    treasures_fished = items_fished['treasure']
    sc_killed = player_stats['pets']['milestone']['sea_creatures_killed']

    # dolphin pet milestone
    pet_milestone_rarity = determine_dolphin_rarity(sc_killed)
    dolphin_milestone_weight = get_dolphin_ms_weight(pet_milestone_rarity)

    # sharks killed
    try:
        sharks_killed = player_leveling['fishing_festival_sharks_killed']
    except:
        sharks_killed = 0
    SHARK_FESTIVAL_MAX = 5000
    progress_shark_festival = min(1, sharks_killed / 5000)
    shark_festival_completion_weight = round(progress_shark_festival * 250)

    # treasure weight
    treasure_weight = round(treasures_fished / 100)


    # pet weight
    # ref_link: https://wiki.hypixel.net/Rarity
    RARITY_TIERS = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary', 'Mythic', 'Divine']

    # ref_linK: https://wiki.hypixel.net/Category:Fishing_Pet
    FISHING_PETS = ['Ammonite', 'Dolphin', 'Baby Yeti', 'Blue Whale', 'Flying Fish', 'Megalodon', 'Penguin', 'Reindeer', 'Spinosaurus', 'Squid']

    def sort_pets_by_rarity(pet_array, tiers):
        return sorted(pet_array, key=lambda x: tiers.index(x.rarity))

    def comparePetRarities(pet1, pet2, tiers):
        return tiers.index(pet1.rarity) - tiers.index(pet2.rarity)

    def comparePetExp(pet1, pet2):
        return max(pet1.exp, pet2.exp)

    class Pet:
        def __init__(self, pet_info):
            self.name = Pet.get_pet_name(pet_info)
            self.rarity = Pet.get_pet_rarity(pet_info)
            self.exp = Pet.get_pet_exp(pet_info)
            self.held_item = Pet.get_pet_held_item(pet_info)
            self.candy_used = Pet.get_pet_candy(pet_info)
            self.true_rarity = Pet.determine_true_rarity(self.rarity, self.held_item)
            self.weight = Pet.get_pet_weight(self.true_rarity)
        
        @staticmethod
        def get_pet_name(info):
            return Pet.format_pet_name(info['type'])

        @staticmethod
        def get_pet_rarity(info):
            return Pet.format_rarity_name(info['tier'])
        
        @staticmethod
        def get_pet_exp(info):
            return info['exp']
        
        @staticmethod
        def get_pet_held_item(info):
            return info['heldItem']
        
        @staticmethod
        def get_pet_candy(info):
            return info['candyUsed']
        
        @staticmethod
        def format_pet_name(giv_name):
            return giv_name.lower().replace('_', ' ').title()
        
        @staticmethod
        def format_rarity_name(giv_rarity):
            return giv_rarity.lower().title()
        
        @staticmethod
        def determine_true_rarity(giv_rarity, giv_held):
            if giv_held == 'PET_ITEM_TIER_BOOST':
                if giv_rarity == 'Uncommon': return 'Common'
                if giv_rarity == 'Rare': return 'Uncommon'
                if giv_rarity == 'Epic': return 'Rare'
                if giv_rarity == 'Legendary': return 'Epic'
                if giv_rarity == 'Mythic': return 'Legendary'
            else:
                return giv_rarity
            
        @staticmethod
        def get_pet_weight(giv_rarity):
            if giv_rarity == 'Common': return 5
            if giv_rarity == 'Uncommon': return 10
            if giv_rarity == 'Rare': return 15
            if giv_rarity == 'Epic': return 20
            if giv_rarity == 'Legendary': return 25
            if giv_rarity == 'Mythic': return 30

    player_pets_array = []
    for pet in player_pet_data:
        player_pets_array.append(Pet(pet_info=pet))


    sorted_pets = sort_pets_by_rarity(player_pets_array, RARITY_TIERS)

    unique_pets = {}
    for pet in sorted_pets:
        if pet.name not in unique_pets:
            unique_pets[pet.name] = pet
        else:
            existing_pet = unique_pets[pet.name]

            # pick the pet with the higher rarity tier
            if comparePetRarities(pet, existing_pet, RARITY_TIERS) > 0:
                unique_pets[pet.name] = pet 

            # pick the highest exp pet
            elif comparePetExp(pet, existing_pet) == pet:
                unique_pets[pet.name] = pet
                
    filtered_pets = list(unique_pets.values())
    player_fishing_pets = [pet for pet in filtered_pets if pet.name in FISHING_PETS]

    unique_pet_weight = sum([pet.weight for pet in player_fishing_pets])


    # TOTAL FISHING WEIGHT 
    grand_total_weight = sum([
        total_fexp_weight, total_fexp_overflow_weight, total_bestiary_weight, total_bestiary_overflow_weight, total_collection_weight, total_tfishi_weight, total_tfishi_overflow_weight, 
        treasure_weight, shark_festival_completion_weight, dolphin_milestone_weight, unique_pet_weight
    ])

    """ WEIGHT OVERVIEW
    print('')
    print('')
    print(f'IGN: {IGN}')
    print('--------------------------------------------------')
    print('WEIGHT OVERVIEW')
    print('--------------------------------------------------')
    print(f'Fishing Exp Weight: {total_fexp_weight}, overflow ({total_fexp_overflow_weight})')
    print(f'Total Fishing BE Weight: {total_bestiary_weight}, overflow ({total_bestiary_overflow_weight})')
    print(f' | Water family: {water_family_weight}, overflow ({water_family_overflow_weight})')
    print(f' | Lava family: {lava_family_weight}, overflow ({lava_family_overflow_weight})')
    print(f' | Spooky family: {spooky_family_weight}, overflow ({spooky_family_overflow_weight})')
    print(f' | Shark family: {shark_family_weight}, overflow ({shark_family_overflow_weight})')
    print(f' | Winter family: {winter_family_weight}, overflow ({winter_family_overflow_weight})')
    print('')
    print(f'Collection Weight: {total_collection_weight}')
    print(f'Trophy Fish Weight: {total_tfishi_weight}, overflow ({total_tfishi_overflow_weight})')
    print(f'Dolphin Pet MS Weight: {dolphin_milestone_weight}')
    print(f'Shark Festival Completion Weight: {shark_festival_completion_weight}')
    print(f'Treasure Weight: {treasure_weight}')
    print(f'Unique Pet Weight: {unique_pet_weight}')
    print('--------------------------------------------------')
    print(f'Grand Total Weight: {grand_total_weight}')
    print('')
    print('')
    """
    
    await ctx.respond(
        f'```md\n'
        f'#--------------------------------------------------#\n'
        f'> {IGN} WEIGHT OVERVIEW\n'
        f'#--------------------------------------------------#\n'
        f'Fishing Exp Weight: {total_fexp_weight} ({total_fexp_overflow_weight} overflow)\n'
        f'\n'
        f'Total Fishing BE Weight: {total_bestiary_weight} ({total_bestiary_overflow_weight} overflow)\n'
        f' | Water family: {water_family_weight} ({water_family_overflow_weight} overflow)\n'
        f' | Lava family: {lava_family_weight} ({lava_family_overflow_weight} overflow)\n'
        f' | Spooky family: {spooky_family_weight} ({spooky_family_overflow_weight} overflow)\n'
        f' | Shark family: {shark_family_weight} ({shark_family_overflow_weight} overflow)\n'
        f' | Winter family: {winter_family_weight} ({winter_family_overflow_weight} overflow)\n'
        f'\n'
        f'Trophy Fish Weight: {total_tfishi_weight} ({total_tfishi_overflow_weight} overflow)\n'
        f'\n'
        f'Collection Weight: {total_collection_weight}\n'
        f'Dolphin Pet MS Weight: {dolphin_milestone_weight}\n'
        f'Shark Festival Completion Weight: {shark_festival_completion_weight}\n'
        f'Treasure Weight: {treasure_weight}\n'
        f'Unique Pet Weight: {unique_pet_weight}\n'
        f'#--------------------------------------------------#\n'
        f'> Grand Total Weight: ({grand_total_weight})\n'
        f'#--------------------------------------------------#\n```'
    )

bot.run()
