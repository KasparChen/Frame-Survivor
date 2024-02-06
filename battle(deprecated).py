import random
import numpy as np

"""
    Weapons
    Chest\Head\Waist
    Foot\Hand 
    Neck
    Ring
[
  ['"Behemoth Tear" Wand of Protection', 2, 19],
  ['Ornate Chestplate', 4, 5],
  ['Full Helm', 2, 6],
  ['Silk Sash', 4, 14],
  ['Hard Leather Boots', 2, 5],
  ['Divine Gloves of Vitriol', 5, 16],
  ['Amulet', 3, 13],
  ['Silver Ring', 2, 1]
  ]
    
    
    设定：
        等阶
        灵性
        能量：蕴含的战力，用于输出与防御
        
        5阶0岁 打不过 4阶5岁
        
        
    
    

    Returns:
        _type_: _description_
"""





# Constants
HEALTH_FACTOR = 10  # HP increase per level of armor
DEF_REDUCTION_FACTOR = 0.1  # How much each DEF point reduces incoming damage
CRIT_MULTIPLIER = 1.5  # Damage multiplier for critical hits
MANA_PER_LEVEL = 5  # Mana increase per level of intelligence

# Calculate total greatness from equipment
def calculate_total_greatness(equipment):
    return sum(item[2] for item in equipment)

# Calculate total level from equipment
def calculate_total_level(equipment):
    return sum(item[1] for item in equipment)



def initialize_character(sloot):
    equipment = sloot['equipment']
    
    
    
    equipment = sloot['equipment']
    """
    equipment has 3 attributes:
         Level: like the position of your job, repersetin the form and base performance (lower and upper limits);
         Greatness: like the final kpi, repersetin the additional performance;
         Enengy: the summary value that works on battel, composed by (constant * level + greatness) , like your final salary.
    
    """
    c_item_lv = 10
    weapon_lv, weapon_g, weapon_e = equipment[0][1], equipment[0][2], c_item_lv * equipment[0][1] + equipment[0][2]
    chest_lv, chest_g, chest_e = equipment[1][1], equipment[1][2], c_item_lv * equipment[1][1] + equipment[1][2]
    head_lv, head_g, head_e = equipment[2][1], equipment[2][2], c_item_lv * equipment[2][1] + equipment[2][2]   
    waist_lv, waist_g, waist_e = equipment[3][1], equipment[3][2], c_item_lv * equipment[3][1] + equipment[3][2]   
    foot_lv, foot_g, foot_e = equipment[4][1], equipment[4][2], c_item_lv * equipment[4][1] + equipment[4][2]
    hand_lv, hand_g, hand_e = equipment[5][1], equipment[5][2], c_item_lv * equipment[5][1] + equipment[5][2]   
    neck_lv, neck_g, neck_e = equipment[6][1], equipment[6][2], c_item_lv * equipment[6][1] + equipment[6][2]   
    ring_lv, ring_g, ring_e = equipment[7][1], equipment[7][2], c_item_lv * equipment[7][1] + equipment[7][2]  

    (10,70)

    # HP = 100*avg(身具|Lv) + sum(身具|灵力)*5 = (100,500)+(0,300) = (100,800)
    HP = 100 * np.average(chest_lv + head_lv + waist_lv) + 5 * np.sum(chest_g + head_g + waist_g) 

    # ATK = 10 + 武器能量 + 手具能量/2 = 10 + (10,70) + (5,35) = (25,125)
    ATK = 10 +  weapon_e + hand_e/2

    # Slipe rate =  (0.05,0.33)
    SLP = 0.4 - hand_lv * 0.07
    
    # Critical rate =  (7,40)
    CTR = 5 + weapon_lv + (ring_e * hand_lv)/10
    
    # DMG 伤害{武器、首饰} = 攻击力 * 状态系数(脱手0.4~0.6/暴击1.5~2/正常0.9~1.1) * 对方减伤系数 + 最终伤害


    # FIN 最终伤害 =  武器|等级 * 满灵数量 + 武器|灵力 / 5  =  (0,44)

    # 出手状态{手套} :
    # 正常概率 = 0.6 + Lv.手具 * 0.08 ; 
    # 脱手概率 = 1 - 正常出手

    # CTR 暴击概率 =  5 + 戒指等级 + 手具等级 +  50% 


    # AGI 敏捷 = 10 + 足具 (等级 * 10 + 灵力) (max 80, min 20)

    # INT 智力 = 10 + 项链|灵力 * 2

    # LUK 运气 = 戒指|等级 * 满灵数量 + 项链|灵力 



    # DEF 减伤系数{胸甲、头盔、腰带} = sum(身具|灵力)*0.1  (max 0.6, min 0)

    
    
    
    character = {
        'HP': 100 + calculate_total_level(equipment) * HEALTH_FACTOR,
        'ATK': 20 + calculate_total_greatness(equipment),
        'CRIT%': 5 + calculate_total_greatness(equipment[:2]) * 0.5,
        'DEF': calculate_total_level(equipment[1:5]) * DEF_REDUCTION_FACTOR,
        'MANA': calculate_total_level(equipment) * MANA_PER_LEVEL,
        # Add more attributes as needed
    }
    return character


def simulate_battle(player, enemy):
    while player['HP'] > 0 and enemy['HP'] > 0:
        # Player's turn
        if random.random() < (player['CRIT%'] / 100):
            damage = player['ATK'] * CRIT_MULTIPLIER
        else:
            damage = player['ATK']
        enemy['HP'] -= max(damage - enemy['DEF'], 0)

        if enemy['HP'] <= 0:
            return 'Player wins'

        # Enemy's turn (similar to player's turn)
        # ...

    return 'Enemy wins' if player['HP'] <= 0 else 'Draw'





def simulate_battle(player_sloot, enemy_sloot):
    player_hp = player_sloot['HP']
    enemy_hp = enemy_sloot['HP']
    player_critical_chance = player_sloot['equipment'][-1][-1] / 100 
    player_critical_multiplier = player_sloot['equipment'][-1][1]
    enemy_critical_chance = enemy_sloot['equipment'][-1][-1] / 100 
    enemy_critical_multiplier = enemy_sloot['equipment'][-1][1]
    
    while player_hp > 0 and enemy_hp > 0:
        # Player's turn 
        if random.random() < player_critical_chance:  
            enemy_hp -= player_sloot['Attack'] * player_critical_multiplier
        else:
            enemy_hp -= player_sloot['Attack']
        
        if enemy_hp <= 0:
            return 1
        
        # Enemy's turn 
        if random.random() < enemy_critical_chance:
            player_hp -= enemy_sloot['Attack'] * enemy_critical_multiplier
        else:
            player_hp -= enemy_sloot['Attack']
        
        if player_hp <= 0:
            return 0
    
    return 2

def estimate_win_chance(player_sloot, enemy_sloot, num_simulations=160): 
    player_wins = 0

    for _ in range(num_simulations):
        if simulate_battle(player_sloot,enemy_sloot) == 'win':
            player_wins +=1

    return int((player_wins / num_simulations) * 100)



"""
def handle_event(player, event):
    if event['type'] == 'treasure':
        if player['INT'] > event['difficulty']:
            # Player succeeds
            pass  # Update game state
        else:
            # Player fails
            pass  # Update game state
    # Handle more event types
    # ...
"""