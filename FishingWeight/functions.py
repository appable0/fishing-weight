
FISHING_MINIONS = ['Clay', 'Fishing']

def get_hunter_level(lvl):
    if lvl == 1: return 'Bronze Hunter'
    if lvl == 2: return 'Silver Hunter'
    if lvl == 3: return 'Gold Hunter'   
    if lvl == 4: return 'Diamond Hunter'

def determine_dolphin_rarity(sc):
    if sc < 250: return 'None'
    if sc >= 250 and sc <1000: return 'Common'
    if sc >= 1000 and sc < 2500: return 'Uncommon'
    if sc >= 2500 and sc < 5000: return 'Rare'
    if sc >= 5000 and sc < 10000: return 'Epic'
    if sc >= 10000: return 'Legendary'
    
def get_dolphin_ms_weight(rarity):
    if rarity == 'None': return 0
    if rarity == 'Common': return 10
    if rarity == 'Uncommon': return 25
    if rarity == 'Rare': return 50
    if rarity == 'Epic': return 75
    if rarity == 'Legendary': return 100

def get_player_fishing_level(player_exp, default_exp_values):
    return max(level for level, exp in default_exp_values.items() if exp <= player_exp)

def percent(part):
    return float(100 * float(part) / float(100))

def format_pet_name(giv_name):
    return giv_name.lower().replace('_', ' ').title()